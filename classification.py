"""Functions related to rock-paper-scissors classification."""

import numpy as np
from scipy.spatial.distance import euclidean

class AngleClassifier:
    def __init__(self, angle_cutoff=90):
        self.angle_cutoff=angle_cutoff

    def arrayify(self, landmark_element):
        """Turns a Mediapipe landmark into an array of its coordinates on the xyz-plane."""
        return np.array([landmark_element.x, landmark_element.y, landmark_element.z])

    def calc_angle(self, finger):
        """Calculates the angle that a finger makes by means of 3 xyz coordinates:
        - finger base
        - finger midpoint (knuckle)
        - finger tip
        """
        a, b, c = finger
        ba = a - b
        bc = c - b

        cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
        angle = np.arccos(cosine_angle)

        return np.degrees(angle)

    def calc_scores_alternate(self, top_fingers_angle, bottom_fingers_angle):
        """Compares the calculated finger angles to "ideal" rock, paper and scissors positions
        to get rockiness, paperiness and scissoriness scores that add up to 100%."""
        rockiness = -1 * (top_fingers_angle + bottom_fingers_angle)
        paperiness = top_fingers_angle + bottom_fingers_angle
        scissoriness = top_fingers_angle - bottom_fingers_angle

        return rockiness, paperiness, scissoriness

    def calc_scores(self, top_fingers_angle, bottom_fingers_angle):
        """Compares the calculated finger angles to "ideal" rock, paper and scissors positions
        to get rockiness, paperiness and scissoriness scores that add up to 100%."""

        top_extendedness = top_fingers_angle - self.angle_cutoff
        bottom_extendedness= bottom_fingers_angle - self.angle_cutoff

        rockiness = -1 * (top_extendedness + bottom_extendedness)
        paperiness = top_extendedness + bottom_extendedness
        scissoriness = top_extendedness - bottom_extendedness

        return rockiness, paperiness, scissoriness

    def predict(self, landmark_array):
        """Will make a rock, paper or scissors classification based on the angle that fingers make.

        Args:
            landmark_array ([type]): Mediapipe landmark detections.
        """
        # Landmark array format is defined by Mediapipe: https://google.github.io/mediapipe/solutions/hands.html
        idx_finger = (
            self.arrayify(landmark_array[8]),  # fingertip
            self.arrayify(landmark_array[6]),  # knuckle
            self.arrayify(landmark_array[5]),  # finger base
        )
        idx_angle = self.calc_angle(idx_finger)

        mid_finger = (
            self.arrayify(landmark_array[12]),
            self.arrayify(landmark_array[10]),
            self.arrayify(landmark_array[9]),
        )
        mid_angle = self.calc_angle(mid_finger)

        top_fingers_angle = (idx_angle + mid_angle) / 2

        ring_finger = (
            self.arrayify(landmark_array[16]),
            self.arrayify(landmark_array[14]),
            self.arrayify(landmark_array[13]),
        )
        ring_angle = self.calc_angle(ring_finger)

        pink_finger = (
            self.arrayify(landmark_array[20]),
            self.arrayify(landmark_array[18]),
            self.arrayify(landmark_array[17]),
        )
        pink_angle = self.calc_angle(pink_finger)

        bottom_fingers_angle = (ring_angle + pink_angle) / 2

        # Are fingers extended or unextended?
        top_extended = top_fingers_angle >= self.angle_cutoff
        bottom_extended = bottom_fingers_angle >= self.angle_cutoff

        if top_extended and bottom_extended:
            pred = 'paper'
        elif top_extended or bottom_extended:
            pred = 'scissors'
        else:
            pred = 'rock'

        rockiness, paperiness, scissoriness = self.calc_scores(
                                                top_fingers_angle,
                                                bottom_fingers_angle,
                                            )
        return top_fingers_angle, bottom_fingers_angle, pred, rockiness, paperiness, scissoriness

class DistanceClassifier:
    def arrayify(self, landmark_element):
        """Turns a Mediapipe landmark into an array of its coordinates on the xyz-plane."""
        return np.array([landmark_element.x, landmark_element.y, landmark_element.z])

    def calc_distances(self, tip, base, palm):
        """Calculates distances from the fingertip to the palm and from the finger base to the palm."""
        dist_tip_palm = euclidean(tip, palm)
        dist_base_palm = euclidean(base, palm)
        return dist_tip_palm, dist_base_palm

    def isextended(self, finger1, finger2, palm):
        """Determines whether a finger is extended or not."""
        dist_tip1_palm, dist_base1_palm = self.calc_distances(finger1[0], finger1[1], palm)
        dist_tip2_palm, dist_base2_palm = self.calc_distances(finger2[0], finger2[1], palm)

        diff_1 = dist_tip1_palm - dist_base1_palm
        diff_2 = dist_tip2_palm - dist_base2_palm

        avg_diff = (diff_1 + diff_2) / 2

        return avg_diff > 0

    def predict(self, landmark_array):
        """Will make a rock, paper or scissors classification based on the relative distances of 
        finger keypoints.

        Args:
            landmark_array ([type]): Mediapipe landmark detections.
        """
        # Landmark array format is defined by Mediapipe: https://google.github.io/mediapipe/solutions/hands.html
        palm = self.arrayify(landmark_array[0])

        idx_finger = (
            self.arrayify(landmark_array[8]),  # fingertip
            self.arrayify(landmark_array[5]),  # finger base
        )

        mid_finger = (
            self.arrayify(landmark_array[12]),
            self.arrayify(landmark_array[9]),
        )

        ring_finger = (
            self.arrayify(landmark_array[16]),
            self.arrayify(landmark_array[13]),
        )

        pink_finger = (
            self.arrayify(landmark_array[20]),
            self.arrayify(landmark_array[17]),
        )

        top_extended = self.isextended(idx_finger, mid_finger, palm)
        bottom_extended = self.isextended(ring_finger, pink_finger, palm)

        if top_extended and bottom_extended:
            pred = 'paper'
        elif top_extended or bottom_extended:
            pred = 'scissors'
        else:
            pred = 'rock'

        return 1, 1, pred, 1, 1, 1
