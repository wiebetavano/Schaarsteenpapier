"""Contains functions to shape what the video stream GUI looks like."""

import numpy as np
from PIL import ImageFont, ImageDraw, Image
import cv2

DETECTION_THICKNESS = 2
DETECTION_FONT_SIZE = 1.0

COUNT_THICKNESS = 2
COUNT_FONT_SIZE = 3.0

FONT = cv2.FONT_HERSHEY_SIMPLEX
GROTESK_FONT_PATH = '/Users/wiebe.tavano/Downloads/rock-paper-scissors-shared-main/rock-paper-scissors-shared-main/helpers/fonts/grotesk_medium.ttf'
FONT = ImageFont.truetype(GROTESK_FONT_PATH, 50)


def putIterationsPerSec(frame, iterations_per_sec):
    """
    Add iterations per second text to lower-left corner of a frame.
    """

    cv2.putText(frame, "{:.0f} iterations/sec".format(iterations_per_sec),
                (0, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255))
    return frame


def putDetection(frame, detection, color):
    """
    Add detection text to lower-left corner of a frame.
    """
    detection_img = cv2.imread(f'/Users/wiebe.tavano/Downloads/rock-paper-scissors-shared-main/rock-paper-scissors-shared-main/helpers/img/{detection}.png', -1)
    frame_width = int(frame.shape[1])
    x_offset = 0
    y_offset = 0

    y1, y2 = y_offset, y_offset + detection_img.shape[0]
    x1, x2 = x_offset, x_offset + detection_img.shape[1]

    alpha_s = detection_img[:, :, 3] / 255.0
    alpha_l = 1.0 - alpha_s

    for c in range(0, 3):
        frame[y1:y2, x1:x2, c] = (alpha_s * detection_img[:, :, c] +
                                alpha_l * frame[y1:y2, x1:x2, c])
    return frame

def putAlert(frame):
    """
    Add the alert remove hand in the middle of the frame
    """
    frame_width = int(frame.shape[1])
    frame_height = int(frame.shape[0])

    img_pil = Image.new('RGBA', [frame_width, frame_height], (0,0,0,0))
    draw = ImageDraw.Draw(img_pil)
    _, _, w1, h1 = draw.textbbox((0, 0), "Hand weg a.u.b", font=ImageFont.truetype(GROTESK_FONT_PATH, 50))
    draw.text(((frame_width-w1)/2, (frame_height-h1)/2), "Hand weg a.u.b", font=ImageFont.truetype(GROTESK_FONT_PATH, 50), fill=(0,255,255))
    _, _, w2, h2 = draw.textbbox((0, 0), "Retire la main s.v.p", font=ImageFont.truetype(GROTESK_FONT_PATH, 30))
    draw.text(((frame_width-w2)/2, (frame_height+h1-h2+30)/2), "Retire la main s.v.p", font=ImageFont.truetype(GROTESK_FONT_PATH, 30), fill=(0,255,255))
    _, _, w3, h3 = draw.textbbox((0, 0), "Remove hand please", font=ImageFont.truetype(GROTESK_FONT_PATH, 30))
    draw.text(((frame_width-w3)/2, (frame_height+h1+h2-h3+60)/2), "Remove hand please", font=ImageFont.truetype(GROTESK_FONT_PATH, 30), fill=(0,255,255))
    img_pil = np.array(img_pil)

    x_offset = 0
    y_offset = 0

    y1, y2 = y_offset, y_offset + img_pil.shape[0]
    x1, x2 = x_offset, x_offset + img_pil.shape[1]

    alpha_s = img_pil[:, :, 3] / 255.0
    alpha_l = 1.0 - alpha_s

    for c in range(0, 3):
        frame[y1:y2, x1:x2, c] = (alpha_s * img_pil[:, :, c] +
                                alpha_l * frame[y1:y2, x1:x2, c])
    return frame

def putCountDown(frame, count):
    """
    Add the countdown in the middle of the frame
    """
    frame_width = int(frame.shape[1])
    frame_height = int(frame.shape[0])

    img_pil = Image.new('RGBA', [frame_width, frame_height], (0,0,0,0))
    draw = ImageDraw.Draw(img_pil)
    _, _, w, h = draw.textbbox((0, 0), str(count), font=FONT)
    draw.text(((frame_width-w)/2, (frame_height-h)/2), str(count), font=FONT, fill=(0,255,255))
    img_pil = np.array(img_pil)

    x_offset = 0
    y_offset = 0

    y1, y2 = y_offset, y_offset + img_pil.shape[0]
    x1, x2 = x_offset, x_offset + img_pil.shape[1]

    alpha_s = img_pil[:, :, 3] / 255.0
    alpha_l = 1.0 - alpha_s

    for c in range(0, 3):
        frame[y1:y2, x1:x2, c] = (alpha_s * img_pil[:, :, c] +
                                alpha_l * frame[y1:y2, x1:x2, c])
    return frame


def putTopAngle(frame, angle):
    """
    Add top fingers angle text to lower-left corner of a frame.
    """

    cv2.putText(frame, f"top angle: {angle}",
                (0, 200), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255))
    return frame

def putBottomAngle(frame, angle):
    """
    Add bottom fingers angle text to lower-left corner of a frame.
    """

    cv2.putText(frame, f"bottom angle: {angle}",
                (0, 150), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255))
    return frame

def putClassLabels(frame):
    """
    Add rock-paper-scissors labels on frame in correct color.
    """

    cv2.putText(frame, f"Rock",
                (0, 200), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255))
    cv2.putText(frame, f"Paper",
                (0, 250), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255))
    cv2.putText(frame, f"Scissors",
                (0, 300), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255))
    return frame
