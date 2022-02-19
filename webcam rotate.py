import cv2
import numpy as np
from cv2 import aruco

from constants import *

if __name__ == '__main__':

    cap = cv2.VideoCapture(0)
    if not (cap.isOpened()):
        print("Could not open video device")
        exit()
    print("Camera found... Start configuration")
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1080)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 810)
    print("Configuration done...")
    cv2.startWindowThread()
    cv2.namedWindow("preview")


    def rot_params_rv(rvecs):
        from math import pi, atan2, asin
        R = cv2.Rodrigues(rvecs)[0]
        roll = 180 * atan2(-R[2][1], R[2][2]) / pi
        pitch = 180 * asin(R[2][0]) / pi
        yaw = 180 * atan2(-R[1][0], R[0][0]) / pi
        rot_params = [roll, pitch, yaw]
        return rot_params


    def estimate_angle(degree):
        myList = [-180, -90, 0, 90, 180]
        x = min(myList, key=lambda x: abs(x - degree))
        if x == -180:
            x = 180
        return x


    while True:
        ret, frame = cap.read()
        # arucoDict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_6X6_50)
        arucoDict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_50)
        arucoParams = cv2.aruco.DetectorParameters_create()
        (corners, ids, rejected) = cv2.aruco.detectMarkers(frame, arucoDict, parameters=arucoParams)

        cam_matrix = np.array([[14492.753623188406, 0, 1024], [0, 14492.753623188406, 1224],
                               [0, 0, 1]])  # camera matrix for f = 50mm with chipsize = 0.00345 mm and 2048x2448px
        dist_coeffs = np.ndarray([0])  # distortion coefficients
        fRvec, fTvec, _obj_points = cv2.aruco.estimatePoseSingleMarkers(corners, 30.0, cam_matrix, dist_coeffs)

        if len(corners) > 0:
            angle = 0
            center = np.zeros((4, 2))
            for i in range(len(ids)):
                realCorners = corners[i].reshape((4, 2))
                center += realCorners
                (topLeft, topRight, bottomRight, bottomLeft) = realCorners
                topRight = (int(topRight[0]), int(topRight[1]))
                bottomRight = (int(bottomRight[0]), int(bottomRight[1]))
                bottomLeft = (int(bottomLeft[0]), int(bottomLeft[1]))
                topLeft = (int(topLeft[0]), int(topLeft[1]))

                line_thickness = 1
                frame = cv2.line(frame, topLeft, topRight, GREEN, line_thickness)
                frame = cv2.line(frame, topRight, bottomRight, GREEN, line_thickness)
                frame = cv2.line(frame, bottomRight, bottomLeft, GREEN, line_thickness)
                frame = cv2.line(frame, bottomLeft, topLeft, GREEN, line_thickness)

                frame = cv2.putText(frame, str(rot_params_rv(fRvec[i])[2]), (topLeft[0], topLeft[1]),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, RED, 1, cv2.LINE_AA)
                frame = cv2.putText(frame, str(estimate_angle(rot_params_rv(fRvec[i])[2])),
                                    (bottomRight[0], bottomRight[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, RED, 1,
                                    cv2.LINE_AA)
                angle += rot_params_rv(fRvec[i])[2]
            if len(ids) == 4:
                center /= 4
                angle /= 4
                x = (np.sum(center, 0) / 4).astype(int)
                frame = cv2.putText(frame, str(estimate_angle(angle)), (x[0], x[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, RED,
                                    1, cv2.LINE_AA)

        cv2.imshow('preview', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
