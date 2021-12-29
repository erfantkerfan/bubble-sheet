import cv2
import numpy as np
import redis
from cv2 import aruco
from cv2 import cv2

from constants import *


class SheetNormalizer:
    IMAGE_HEIGHT = 1100

    def __init__(self, image, visual=False):
        self.image = image
        self.visual = visual
        self.load_image()
        self.get_border()
        self.four_point_transform()

    # read and resize image
    def load_image(self):
        # w = int(round(self.IMAGE_HEIGHT * self.image.shape[1] / self.image.shape[0]))
        # self.frame = cv2.resize(self.image, (w, self.IMAGE_HEIGHT), interpolation=cv2.INTER_LANCZOS4)
        self.frame = self.image

        # arucoDict = aruco.Dictionary_get(cv2.aruco.DICT_6X6_50)
        arucoDict = aruco.Dictionary_get(cv2.aruco.DICT_4X4_50)
        arucoParams = aruco.DetectorParameters_create()
        (self.markers, self.ids, rejected) = aruco.detectMarkers(self.frame, arucoDict, parameters=arucoParams)

        if self.visual:
            cv2.imshow('preview', self.frame)
            cv2.waitKey(0)

    def get_border(self):
        depth = 0
        top_left_mark = self.markers[np.where(self.ids == 1)[depth][depth]]
        top_right_mark = self.markers[np.where(self.ids == 2)[depth][depth]]
        bottom_left_mark = self.markers[np.where(self.ids == 3)[depth][depth]]
        bottom_right_mark = self.markers[np.where(self.ids == 4)[depth][depth]]

        x, y = 0, 1
        top_left_corner = (top_left_mark[depth][3][x], top_left_mark[depth][3][y])
        top_right_corner = (top_right_mark[depth][2][x], top_right_mark[depth][2][y])
        bottom_left_corner = (bottom_left_mark[depth][0][x], bottom_left_mark[depth][0][y])
        bottom_right_corner = (bottom_right_mark[depth][1][x], bottom_right_mark[depth][1][y])

        self.borders = np.array([top_left_corner, top_right_corner, bottom_right_corner, bottom_left_corner])

        if self.visual:
            self.highlight_corners()

    def highlight_corners(self):
        radius = 2
        thickness = 2
        self.frame = cv2.circle(self.frame, (int(self.borders[0][0]), int(self.borders[0][1])), radius, BLUE,
                                thickness)
        self.frame = cv2.circle(self.frame, (int(self.borders[1][0]), int(self.borders[1][1])), radius, BLUE,
                                thickness)
        self.frame = cv2.circle(self.frame, (int(self.borders[2][0]), int(self.borders[2][1])), radius, BLUE,
                                thickness)
        self.frame = cv2.circle(self.frame, (int(self.borders[3][0]), int(self.borders[3][1])), radius, BLUE,
                                thickness)
        cv2.imshow('preview', self.frame)
        cv2.waitKey(0)

    def four_point_transform(self):
        (tl, tr, br, bl) = self.borders
        # compute the width of the new image, which will be the
        # maximum distance between bottom-right and bottom-left
        # x-coordiates or the top-right and top-left x-coordinates
        widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
        widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
        maxWidth = max(int(widthA), int(widthB))
        # compute the height of the new image, which will be the
        # maximum distance between the top-right and bottom-right
        # y-coordinates or the top-left and bottom-left y-coordinates
        heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
        heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
        maxHeight = max(int(heightA), int(heightB))
        # now that we have the dimensions of the new image, construct
        # the set of destination points to obtain a "birds eye view",
        # (i.e. top-down view) of the image, again specifying points
        # in the top-left, top-right, bottom-right, and bottom-left
        # order
        dst = np.array([
            [0, 0],
            [maxWidth - 1, 0],
            [maxWidth - 1, maxHeight - 1],
            [0, maxHeight - 1]], dtype="float32")
        # compute the perspective transform matrix and then apply it
        matrix = cv2.getPerspectiveTransform(self.borders, dst)
        # warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
        self.frame = cv2.warpPerspective(self.frame, matrix, (maxWidth, maxHeight), cv2.INTER_LINEAR,
                                         borderMode=cv2.BORDER_CONSTANT,
                                         borderValue=(0, 0, 0))
        if self.visual:
            cv2.imshow('preview', self.frame)
            cv2.waitKey(0)

    def get_adaptive_thresh(self):
        w = int(round(self.IMAGE_HEIGHT * self.frame.shape[1] / self.frame.shape[0]))
        self.frame = cv2.resize(self.frame, (w, self.IMAGE_HEIGHT), interpolation=cv2.INTER_LANCZOS4)
        temp = cv2.cvtColor(self.frame, cv2.COLOR_RGB2GRAY)
        self.frame_tresh = cv2.adaptiveThreshold(temp, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 95,
                                                 7)
        self.frame = cv2.bitwise_not(self.frame_tresh)

        if self.visual:
            cv2.imshow('preview', self.frame)
            cv2.waitKey(0)
            try:
                cv2.destroyAllWindows()
            except Exception:
                pass
        return self.frame, self.frame_tresh


class BubbleReader:
    MIN_AREA = 220
    MIN_AREA_WITH_TRESH = 200
    MIN_CIRCULARITY = 0.6
    MIN_CONVEXITY = 0.7
    MIN_INERTIA_RATIO = 0.15
    MIN_DIST_BETWEEN_BLOBS = 13
    QUESTION_COLUMNS = 6
    QUESTION_ROWS = 50
    BUBBLE_PER_QUESTION = 4

    def __init__(self, sheet, sheet_tresh, with_markers=False, visual=False):
        self.image = sheet
        self.image_tresh = sheet_tresh
        self.visual = visual
        self.with_markers = with_markers
        self.bubble_count = self.QUESTION_COLUMNS * self.QUESTION_ROWS * self.BUBBLE_PER_QUESTION

    def make_detector(self, tresh=False):
        # Set our filtering parameters
        # Initialize parameter setting using cv2.SimpleBlobDetector
        params = cv2.SimpleBlobDetector_Params()

        # Set Area filtering parameters
        params.filterByArea = True
        if tresh:
            params.minArea = self.MIN_AREA_WITH_TRESH
        else:
            params.minArea = self.MIN_AREA

        # Set Circularity filtering parameters
        params.filterByCircularity = True
        params.minCircularity = self.MIN_CIRCULARITY

        # Set Convexity filtering parameters
        params.filterByConvexity = True
        params.minConvexity = self.MIN_CONVEXITY

        # Set inertia filtering parameters
        params.filterByInertia = True
        params.minInertiaRatio = self.MIN_INERTIA_RATIO

        params.filterByInertia = True

        params.minDistBetweenBlobs = self.MIN_DIST_BETWEEN_BLOBS

        # Create a detector with the parameters
        detector = cv2.SimpleBlobDetector_create(params)

        return detector

    def detect_answers(self):
        # Detect filled blobs
        keypoints_filled = self.make_detector().detect(self.image)

        # Detect empty blobs
        keypoints_empty = self.make_detector(tresh=True).detect(self.image_tresh)
        keypoints = keypoints_filled + keypoints_empty
        number_of_valid_keypoints = self.BUBBLE_PER_QUESTION * self.QUESTION_ROWS * self.QUESTION_COLUMNS
        if len(keypoints) != number_of_valid_keypoints:
            raise Exception("number of keypoints not valid")

        return keypoints, keypoints_filled, keypoints_empty

    def extract_choices(self, keypoints, keypoints_filled, keypoints_empty):
        choices = list()
        sorted_keypoints = list(sorted(keypoints, key=lambda x: (int(x.pt[1]), int(x.pt[0]))))
        for row in range(self.QUESTION_ROWS):
            whole_row = list(sorted(sorted_keypoints[
                                    row * (self.QUESTION_COLUMNS * self.BUBBLE_PER_QUESTION): (row + 1) * (
                                            self.QUESTION_COLUMNS * self.BUBBLE_PER_QUESTION)],
                                    key=lambda x: (int(x.pt[0]), int(x.pt[1]))))
            if self.visual:
                blobs = cv2.drawKeypoints(self.image, whole_row, np.zeros((1, 1)), BLUE,
                                          cv2.DRAW_MATCHES_FLAGS_NOT_DRAW_SINGLE_POINTS)
                blobs = cv2.drawKeypoints(blobs, whole_row, np.zeros((1, 1)), RED,
                                          cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
                cv2.imshow("Filtering Circular Blobs Only", blobs)
                cv2.waitKey(10)
            for column in range(self.QUESTION_COLUMNS):
                question = whole_row[column * self.BUBBLE_PER_QUESTION: (column + 1) * self.BUBBLE_PER_QUESTION]
                choice = []
                flag = 0
                for i, bubble in enumerate(question):
                    if bubble in keypoints_filled:
                        choice.append(i + 1)
                        flag += 1
                choices.append(choice)
        if self.visual or self.with_markers:
            blobs = cv2.drawKeypoints(self.image, keypoints_filled, np.zeros((1, 1)), GREEN,
                                      cv2.DRAW_MATCHES_FLAGS_NOT_DRAW_SINGLE_POINTS)
            blobs = cv2.drawKeypoints(blobs, keypoints_filled, np.zeros((1, 1)), GREEN,
                                      cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
            blobs = cv2.drawKeypoints(blobs, keypoints_empty, np.zeros((1, 1)), RED,
                                      cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
            self.sheet_with_answers = blobs
            if self.visual:
                cv2.imshow("Filtering Circular Blobs Only", blobs)
                cv2.waitKey(0)
        # We do a bit of magic here
        choices.append(['ErfanTKErfan'])
        arr_2d = np.reshape(np.delete(np.array(choices, dtype=object), -1),
                            (self.QUESTION_ROWS, self.QUESTION_COLUMNS)).transpose().flatten().tolist()
        return arr_2d

    def get_sheet_with_choices(self):
        if self.visual or (self.with_markers and self.sheet_with_answers is not None):
            return self.sheet_with_answers
        else:
            raise Exception("sheet with answers has not been generated")


def establish_redis():
    return redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
