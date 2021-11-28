import cv2
import numpy as np
from cv2 import aruco
from cv2 import cv2


class SheetNormalizer:
    IMAGE_WIDTH = 1200

    def __init__(self, image, visual=False):
        self.image = image
        self.visual = visual
        self.load_image()
        self.get_border()

        if len(self.markers) == 4:
            self.get_border()
            if self.visual:
                self.highlight_corners()
            self.four_point_transform()
            self.get_adaptive_thresh()
        else:
            print('4 corner markers not found')

        try:
            cv2.destroyAllWindows()
        except Exception:
            pass

    # read and resize image
    def load_image(self):
        h = int(round(self.IMAGE_WIDTH * self.image.shape[0] / self.image.shape[1]))
        self.frame = cv2.resize(self.image, (self.IMAGE_WIDTH, h), interpolation=cv2.INTER_LANCZOS4)

        arucoDict = aruco.Dictionary_get(cv2.aruco.DICT_6X6_50)
        # arucoDict = aruco.Dictionary_get(cv2.aruco.DICT_4X4_50)
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

    def highlight_corners(self):
        radius = 2
        color = (255, 0, 0)
        thickness = 2
        self.frame = cv2.circle(self.frame, (int(self.borders[0][0]), int(self.borders[0][1])), radius, color,
                                thickness)
        self.frame = cv2.circle(self.frame, (int(self.borders[1][0]), int(self.borders[1][1])), radius, color,
                                thickness)
        self.frame = cv2.circle(self.frame, (int(self.borders[2][0]), int(self.borders[2][1])), radius, color,
                                thickness)
        self.frame = cv2.circle(self.frame, (int(self.borders[3][0]), int(self.borders[3][1])), radius, color,
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
        frame = cv2.cvtColor(self.frame, cv2.COLOR_RGB2GRAY)
        self.frame = cv2.adaptiveThreshold(frame, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 51, 7)

        if self.visual:
            cv2.imshow('preview', self.frame)
            cv2.waitKey(0)
