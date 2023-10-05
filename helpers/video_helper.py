import logging
import time
from datetime import datetime
from threading import Thread
from typing import List

import cv2
import mediapipe as mp
import numpy as np

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(threadName)s %(message)s')


class CountsPerSec:
    """
    Class that tracks the number of occurrences ("counts") of an
    arbitrary event and returns the frequency in occurrences
    (counts) per second. The caller must increment the count.
    """

    def __init__(self):
        self._start_time = None
        self._num_occurrences = 0

    def start(self):
        self._start_time = datetime.now()
        return self

    def increment(self):
        self._num_occurrences += 1

    def countsPerSec(self):
        elapsed_time = (datetime.now() - self._start_time).total_seconds()
        return self._num_occurrences / elapsed_time if elapsed_time > 0 else 0


class VideoGetter:
    """
    Class that continuously gets frames from a VideoCapture object
    with a dedicated thread.
    """

    def __init__(self, src=0):
        self.logger = logging.getLogger('VideoGetter')
        self.stream = cv2.VideoCapture(src)
        self.stream.set(cv2.CAP_PROP_FPS, 100)
        cv2.namedWindow('Video', cv2.WINDOW_FULLSCREEN)
        (self.grabbed, self.frame) = self.stream.read()
        self.stopped = False

    def start(self):
        Thread(target=self.get, args=()).start()
        return self

    def get(self):
        while not self.stopped:
            if not self.grabbed or self.frame is None:
                self.logger.error("Can't find image! Perhaps camera is disconnected?")
                self.stop()
            else:
                (self.grabbed, self.frame) = self.stream.read()

    def stop(self):
        self.stopped = True


class VideoProcessor:
    """
    Class that continuously processes images with mediapipe
    with a dedicated thread.
    """

    def __init__(self, classifier, model_complexity=1, min_detection_confidence=0.5,\
                min_tracking_confidence=0.5, paper_color_intensity=1.5, scissor_color_intensity=1, \
                rock_color_intensity=1):
        self.logger = logging.getLogger('VideoProcessor')
        self.mp_hands = mp.solutions.hands
        self.hand_detector = self.mp_hands.Hands(
                model_complexity=model_complexity,
                static_image_mode=False,
                max_num_hands=1,
                min_detection_confidence=min_detection_confidence,
                min_tracking_confidence=min_tracking_confidence
        )
        self.mp_drawing = mp.solutions.drawing_utils
        self.classifier = classifier
        self.stopped = False
        self.paper_color_intensity = paper_color_intensity
        self.scissor_color_intensity = scissor_color_intensity
        self.rock_color_intensity = rock_color_intensity

    def process(self, frame):
        start_hand = time.time()
        results = self.hand_detector.process(frame)
        self.logger.debug(f'hand: {time.time() - start_hand}')

        if not results.multi_hand_landmarks:
            return

        if len(results.multi_hand_landmarks) > 1:
            print('No more than 1 hand please!')
            return

        hand_landmarks = results.multi_hand_landmarks[0]

        start_detect = time.time()
        topangle, bottomangle, pred, rockiness, paperiness, scissoriness = self.classifier.predict(hand_landmarks.landmark)

        color = self.mp_drawing.DrawingSpec()
        output_color = (
            rockiness * self.rock_color_intensity, 
            scissoriness * self.scissor_color_intensity, 
            paperiness * self.paper_color_intensity
        )
        color.color = output_color

        self.mp_drawing.draw_landmarks(
            image=frame,
            landmark_list=hand_landmarks,
            connections=self.mp_hands.HAND_CONNECTIONS,
            landmark_drawing_spec=color,
            connection_drawing_spec=color,
        )

        self.logger.debug(f'detect: {time.time() - start_detect}')
        return topangle, bottomangle, pred, output_color

    def close(self):
        self.hand_detector.close()


class VideoShower:
    """
    Class that continuously shows a frame using a dedicated thread.
    """

    def __init__(self, frame=None):
        self.frame = frame
        self.stopped = False

    def show(self):
        if self.frame is None:
            logging.error("Found empty frame! Can't visualise")

        cv2.imshow("Video", self.frame)
        if cv2.waitKey(1) == ord("q"):
            self.stopped = True

    def stop(self):
        self.stopped = True

def search_for_camera() -> List[int]:
    """Will search for all connected cameras.

    Returns:
        List[int]: Sources with a responding external camera.
    """
    available_cameras = []

    for camera_idx in range(20):
        cap = cv2.VideoCapture(camera_idx)
        if cap.isOpened():
            print(f'Camera index available: {camera_idx}')
            available_cameras.append(camera_idx)
            cap.release()
    if available_cameras:
        return available_cameras
    else:
        print('Could not find any connected camera!')
        return None
