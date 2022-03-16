import os
import glob
import argparse
from itertools import combinations

import cv2
import yaml
import numpy as np
import matplotlib.pyplot as plt


class Pose:
    @classmethod
    def from_axis_angle(cls, r, t):
        return Pose(cv2.Rodrigues(np.array(r))[0], np.array(t))

    def __init__(self, r, t):
        self.r = r
        self.t = t

    @property
    def I(self):
        return Pose(self.r.T, - (self.r.T @ self.t))

    def __matmul__(self, other):
        return Pose(self.r @ other.r, self.r @ other.t + self.t)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get rectification maps from camcalib config')
    parser.add_argument('--config', '-c', help='choose a camcalib config file', required=True)
    parser.add_argument('--data', '-d', help='folder with image data (calibration folder)', required=True)
    args = parser.parse_args()

    config_file = args.config
    data = args.data
    if not os.path.isdir(data):
        raise Exception("Could not find any data in: " + data + ". Check the path to your images and try again.")

    config = yaml.load(open(config_file, 'r'), Loader=yaml.Loader)

    cams = list(config['sensors'].keys())
    cam_pair = [cams[0], cams[1]]
    cam0, cam1 = cam_pair
    print("Rectifying " + cam0 + " and " + cam1 + "...")

    cam0_calib = config['sensors'][cam0]
    cam1_calib = config['sensors'][cam1]

    cam0_intrinsics = cam0_calib['intrinsics']['parameters']
    cam1_intrinsics = cam1_calib['intrinsics']['parameters']
    if cam0_calib['intrinsics']['type'] == 'PinholeRadTan' and cam1_calib['intrinsics']['type'] == 'PinholeRadTan':
        cv = cv2
        dist_keys = ['k1', 'k2', 'p1', 'p2']
    elif cam0_calib['intrinsics']['type'] == 'KannalaBrandt' and cam1_calib['intrinsics']['type'] == 'KannalaBrandt':
        cv = cv2.fisheye
        dist_keys = ['k1', 'k2', 'k3', 'k4']
    else:
        raise "Opencv cannot handle these camera models"

    P_c0 = Pose.from_axis_angle(cam0_calib['extrinsics']['axis_angle'], cam0_calib['extrinsics']['translation'])
    P_c1 = Pose.from_axis_angle(cam1_calib['extrinsics']['axis_angle'], cam1_calib['extrinsics']['translation'])

    P_c1_c0 = P_c1 @ P_c0.I
    imsize = cam0_intrinsics['image_size']
    camera_matrix_c0 = np.array([[cam0_intrinsics['fx'], 0, cam0_intrinsics['cx']],
                                 [0, cam0_intrinsics['fy'], cam0_intrinsics['cy']],
                                 [0, 0, 1]])
    camera_matrix_c1 = np.array([[cam1_intrinsics['fx'], 0, cam1_intrinsics['cx']],
                                 [0, cam1_intrinsics['fy'], cam1_intrinsics['cy']],
                                 [0, 0, 1]])
    cam0_intrinsics_dist = np.array([cam0_intrinsics[k] for k in dist_keys])
    cam1_intrinsics_dist = np.array([cam1_intrinsics[k] for k in dist_keys])


    R1, R2, P1, P2, Q, validPixROI1, validPixROI2 = cv.stereoRectify(camera_matrix_c0, cam0_intrinsics_dist,
                                                                     camera_matrix_c1, cam1_intrinsics_dist,
                                                                     imsize, P_c1_c0.r, P_c1_c0.t)
    rect_map0 = cv.initUndistortRectifyMap(camera_matrix_c0, cam0_intrinsics_dist, R1, P1, imsize, cv2.CV_16SC2)
    rect_map1 = cv.initUndistortRectifyMap(camera_matrix_c1, cam1_intrinsics_dist, R2, P2, imsize, cv2.CV_16SC2)

    imgs = {s: sorted(glob.glob(data + '/' + s + '/*')) for s in cam_pair}
    for s1, s2 in combinations(cam_pair, 2):
        for img_f_s1, img_f_s2 in zip(imgs[s1], imgs[s2]):
            img_s1 = cv2.remap(cv2.imread(img_f_s1), *rect_map0, cv2.INTER_LANCZOS4)
            img_s2 = cv2.remap(cv2.imread(img_f_s2), *rect_map1, cv2.INTER_LANCZOS4)

            plt.imshow(np.hstack((img_s1[:, validPixROI1[0]:validPixROI1[0] + validPixROI1[2]],
                                  img_s2[:, validPixROI2[0]:validPixROI2[0] + validPixROI2[2]])))
            plt.show()
