import logging
from re import A
import threading
import time
import webbrowser

import av
import streamlit as st
from streamlit_webrtc import (RTCConfiguration, VideoProcessorBase, WebRtcMode,
                              webrtc_streamer)

import config as cfg
from classification import AngleClassifier, DistanceClassifier
from connection import Connection
from helpers.arduino_io import ArduinoLink
from helpers.gui_helper import (putBottomAngle, putClassLabels, putCountDown,
                                putDetection, putTopAngle, putAlert)
from helpers.video_helper import VideoProcessor

logger = logging.getLogger(__name__)

RTC_CONFIGURATION = RTCConfiguration({"iceServers": []})

if cfg.PHYSICAL and not Connection.connection:
    Connection.connection = True
    ARDUINO_LINK = ArduinoLink()
    ARDUINO_LINK.test_ports()
    Connection.link = ARDUINO_LINK
else:
    ARDUINO_LINK = Connection.link

def main():
    st.header("✋ ✌️ ✊ 🤖")

    freestyle_mode_page = "Freestyle Mode"
    game_mode_page = "Game mode"

    app_mode = st.sidebar.selectbox(
        "Mode:",
        [
            game_mode_page,
            freestyle_mode_page
        ],
    )
    st.subheader(app_mode)

    if app_mode == game_mode_page:
        app_game_mode()
    elif app_mode == freestyle_mode_page:
        app_freestyle_mode()

    logger.debug("=== Alive threads ===")
    for thread in threading.enumerate():
        if thread.is_alive():
            logger.debug(f"  {thread.name} ({thread.ident})")


def app_loopback():
    """ Simple video loopback """
    webrtc_streamer(key="loopback")


def app_game_mode():
    """RPS freestyle mode page"""
    class GameMode(VideoProcessorBase):
        def __init__(self):
            """
            Runs inference and visualization streaming pipeline.
            """
            self.count = time.time()
            self.last_freeze = 0
            self.last_too_fast = 0
            self.freeze_frame = None
            self.classifier = AngleClassifier(angle_cutoff=cfg.ANGLE_CUTOFF_GAME)  # seems to be the best classifier

            self.video_processor = VideoProcessor(
                classifier=self.classifier, \
                model_complexity=cfg.MODEL_COMPLEXITY, \
                min_detection_confidence=cfg.MIN_DETECTION_CONFIDENCE_GAME, \
                min_tracking_confidence=cfg.MIN_TRACKING_CONFIDENCE_GAME, \
                paper_color_intensity=cfg.PAPER_COLOR_INTENSITY, \
                scissor_color_intensity=cfg.SCISSOR_COLOR_INTENSITY, \
                rock_color_intensity=cfg.ROCK_COLOR_INTENSITY
            )

        def _do_physical(self, pred):
            if pred == 'rock':
                ARDUINO_LINK.write(b'P')
            elif pred == 'scissors':
                ARDUINO_LINK.write(b'R')
            elif pred == 'paper':
                ARDUINO_LINK.write(b'S')

        def _annotate_image(self, frame, pred, topangle, bottomangle, output_color):
            if cfg.DISPLAY_ANGLES:
                frame = putTopAngle(frame, topangle)
                frame = putBottomAngle(frame, bottomangle)
            if cfg.DISPLAY_CLASS_LABELS:
                frame = putClassLabels(frame)
            if cfg.VERBOSE:
                logging.info(pred)
            if cfg.DISPLAY_DETECTION:
                frame = putDetection(frame, pred, output_color)

            return frame

        def _countdown(self):
            time_diff = abs(time.time() - self.count)
            if time_diff < (cfg.COUNT_FROM-1):
                return True, ((cfg.COUNT_FROM) - round(time_diff))
            else:
                return False, None

        def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
            if time.time() - self.last_freeze > cfg.DELAY:  # is last detection long enough ago to stop freeze frame & start new game?

                frame = frame.to_ndarray(format="bgr24")

                if time.time() - self.last_too_fast < cfg.TOO_FAST_DELAY:  # is last too fast detection long enough ago to start new game?
                    frame = putAlert(frame)
                    return av.VideoFrame.from_ndarray(frame, format="bgr24")

                results = self.video_processor.process(frame)  # detect hands
                is_countdown, time_diff = self._countdown()

                if is_countdown:
                    if results:  # detected hands during countdown (too fast)
                        frame = putAlert(frame)
                        self.count = time.time() + cfg.TOO_FAST_DELAY  # restart countdown
                        self.last_too_fast = time.time()
                        return av.VideoFrame.from_ndarray(frame, format="bgr24")
                    else:
                        frame = putCountDown(frame, time_diff)
                else:
                    if results:  # found results after countown
                        topangle, bottomangle, pred, output_color = results

                        if cfg.PHYSICAL:
                            self._do_physical(pred=pred)

                        frame = self._annotate_image(frame=frame, pred=pred, topangle=topangle, \
                            bottomangle=bottomangle, output_color=output_color)

                        self.count = time.time() + cfg.DELAY
                        self.last_freeze = time.time()
                        self.freeze_frame = av.VideoFrame.from_ndarray(frame, format="bgr24")

                return av.VideoFrame.from_ndarray(frame, format="bgr24")
            else: # still in delay period
                return self.freeze_frame

    _ = webrtc_streamer(
        key="object-detection",
        mode=WebRtcMode.SENDRECV,
        rtc_configuration=RTC_CONFIGURATION,
        video_processor_factory=GameMode,
        media_stream_constraints={"video": True, "audio": False},
        async_processing=True,
    )


class Cache():
    def __init__(self, now, result):
        self.time = now
        self.result = result

    def update(self, now, result):
        self.time = now
        self.result = result


def app_freestyle_mode():
    """RPS freestyle mode page"""
    class FreeStyleMode(VideoProcessorBase):
        def __init__(self):
            """
            Runs inference and visualization streaming pipeline.
            """
            self.cache = Cache(now=1, result='')
            self.classifier = AngleClassifier(angle_cutoff=cfg.ANGLE_CUTOFF_FREESTYLE)  # seems to be the best classifier

            self.video_processor = VideoProcessor(
                classifier=self.classifier, \
                model_complexity=cfg.MODEL_COMPLEXITY, \
                min_detection_confidence=cfg.MIN_DETECTION_CONFIDENCE_FREESTYLE, \
                min_tracking_confidence=cfg.MIN_TRACKING_CONFIDENCE_FREESTYLE, \
                paper_color_intensity=cfg.PAPER_COLOR_INTENSITY, \
                scissor_color_intensity=cfg.SCISSOR_COLOR_INTENSITY, \
                rock_color_intensity=cfg.ROCK_COLOR_INTENSITY
            )

        def _annotate_image(self, frame, pred, topangle, bottomangle, output_color):
            if cfg.DISPLAY_ANGLES:
                frame = putTopAngle(frame, topangle)
                frame = putBottomAngle(frame, bottomangle)
            if cfg.DISPLAY_CLASS_LABELS:
                frame = putClassLabels(frame)
            if cfg.VERBOSE:
                logging.info(pred)
            if cfg.DISPLAY_DETECTION:
                frame = putDetection(frame, pred, output_color)

            return frame

        def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
            frame = frame.to_ndarray(format="bgr24")

            results = self.video_processor.process(frame)

            if results:
                topangle, bottomangle, pred, output_color = results

                if cfg.PHYSICAL:
                    time_since_cache = abs(time.time() - self.cache.time)
                    if (time_since_cache > cfg.CACHE_TIME) and (pred != self.cache.result): # only send instruction after cache time & if different than cached instruction
                        if ARDUINO_LINK and pred == 'rock':
                            ARDUINO_LINK.write(b'P')
                        elif ARDUINO_LINK and pred == 'paper':
                            ARDUINO_LINK.write(b'S')
                        elif ARDUINO_LINK and pred == 'scissors':
                            ARDUINO_LINK.write(b'R')
                        self.cache.update(now=time.time(), result=pred)

                frame = self._annotate_image(frame=frame, pred=pred, topangle=topangle, \
                    bottomangle=bottomangle, output_color=output_color)

            return av.VideoFrame.from_ndarray(frame, format="bgr24")

    _ = webrtc_streamer(
        key="object-detection",
        mode=WebRtcMode.SENDRECV,
        rtc_configuration=RTC_CONFIGURATION,
        video_processor_factory=FreeStyleMode,
        media_stream_constraints={"video": True, "audio": False},
        async_processing=True,
    )

if __name__ == "__main__":
    import os

    DEBUG = os.environ.get("DEBUG", "false").lower() not in ["false", "no", "0"]

    logging.basicConfig(
        format="[%(asctime)s] %(levelname)7s from %(name)s in %(pathname)s:%(lineno)d: "
        "%(message)s",
        force=True,
    )

    logger.setLevel(level=logging.DEBUG if DEBUG else logging.INFO)

    st_webrtc_logger = logging.getLogger("streamlit_webrtc")
    st_webrtc_logger.setLevel(logging.DEBUG)

    fsevents_logger = logging.getLogger("fsevents")
    fsevents_logger.setLevel(logging.WARNING)

    main()
