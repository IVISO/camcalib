#!/usr/bin/env python3
"""Rectify a stereo pair from a camcalib result with OpenCV.

    python rectify.py --config result.yaml --data recording/ --cameras /cam0 /cam1 --out rectified/

Reads a camcalib result YAML (camcalib 2.0, or a 1.x file), picks two cameras, computes the
rectification maps and shows or writes the rectified image pairs side by side with a few
horizontal lines drawn across both: after a good calibration a point lies on the same line in
both images.

The recording folder holds one sub-folder of images per camera, named like the stream without
its leading slash (recording/cam0/*.png). Images are paired by their order in the folders.

Models: Pinhole and PinholeRadTan4/5/8 go through cv2.stereoRectify, KannalaBrandt through
cv2.fisheye. Both cameras must use the same kind. Omnidirectional has no stereo rectification
in OpenCV.
"""
import argparse
import glob
import os
import sys

import cv2
import numpy as np
import yaml

# camera model -> (OpenCV module, distortion coefficients in OpenCV's order)
MODELS = {
    "Pinhole": (cv2, []),
    "PinholeRadTan": (cv2, ["k1", "k2", "p1", "p2", "k3", "k4", "k5", "k6"]),   # camcalib 1.x name; absent coefficients are 0
    "PinholeRadTan4": (cv2, ["k1", "k2", "p1", "p2"]),
    "PinholeRadTan5": (cv2, ["k1", "k2", "p1", "p2", "k3"]),
    "PinholeRadTan8": (cv2, ["k1", "k2", "p1", "p2", "k3", "k4", "k5", "k6"]),
    "KannalaBrandt": (cv2.fisheye, ["k1", "k2", "k3", "k4"]),
}
IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".bmp")


def pose(extrinsics):
    """4x4 matrix of an extrinsics block: axis-angle and translation, reference -> sensor."""
    T = np.eye(4)
    T[:3, :3] = cv2.Rodrigues(np.asarray(extrinsics["axis_angle"], dtype=float))[0]
    T[:3, 3] = np.asarray(extrinsics["translation"], dtype=float)
    return T


def cameras_in(result):
    """Names of the camera sensors; 1.x files have no 'type' and hold cameras only."""
    return [name for name, sensor in result["sensors"].items()
            if sensor.get("type", "CAMERA") == "CAMERA" and "intrinsics" in sensor]


def camera_matrix(p):
    return np.array([[p["fx"], 0.0, p["cx"]], [0.0, p["fy"], p["cy"]], [0.0, 0.0, 1.0]])


def image_files(data, stream):
    folder = os.path.join(data, stream.lstrip("/"))
    files = sorted(f for f in glob.glob(os.path.join(folder, "*")) if f.lower().endswith(IMAGE_EXTENSIONS))
    if not files:
        sys.exit(f"No images in {folder}.")
    return files


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--config", "-c", required=True, help="camcalib result YAML")
    ap.add_argument("--data", "-d", required=True, help="folder with one sub-folder of images per camera")
    ap.add_argument("--cameras", nargs=2, metavar=("LEFT", "RIGHT"),
                    help="the two camera streams (default: the first two cameras of the result)")
    ap.add_argument("--out", "-o", help="write the rectified pairs as PNG files into this folder")
    ap.add_argument("--no-show", action="store_true", help="do not open a window per pair")
    args = ap.parse_args()

    with open(args.config) as f:
        result = yaml.safe_load(f)
    cameras = cameras_in(result)
    if len(cameras) < 2:
        sys.exit(f"{args.config} holds {len(cameras)} camera(s); rectification needs two with extrinsics.")
    left, right = args.cameras or cameras[:2]
    for name in (left, right):
        if name not in cameras:
            sys.exit(f"{name} is not a camera in {args.config}. Cameras: {', '.join(cameras)}")
        if "extrinsics" not in result["sensors"][name]:
            sys.exit(f"{name} has no extrinsics; an intrinsic-only result cannot be rectified.")

    sensors = [result["sensors"][name] for name in (left, right)]
    types = [s["intrinsics"]["type"] for s in sensors]
    for t in types:
        if t not in MODELS:
            sys.exit(f"OpenCV has no stereo rectification for the {t} model.")
    if MODELS[types[0]][0] is not MODELS[types[1]][0]:
        sys.exit(f"{left} ({types[0]}) and {right} ({types[1]}) need different OpenCV models; "
                 "rectify two cameras of one kind.")
    cv = MODELS[types[0]][0]

    K, D = [], []
    for sensor, t in zip(sensors, types):
        p = sensor["intrinsics"]["parameters"]
        K.append(camera_matrix(p))
        keys = MODELS[t][1]
        D.append(np.array([p.get(k, 0.0) for k in keys], dtype=float) if keys else np.zeros(4))
    sizes = [tuple(int(v) for v in s["intrinsics"]["parameters"]["image_size"]) for s in sensors]
    if sizes[0] != sizes[1]:
        sys.exit(f"Both cameras must have the same image size ({sizes[0]} and {sizes[1]}).")
    size = sizes[0]

    # Pose of the right camera in the left camera's frame: P_RL = P_RE * P_LE^-1.
    T_rl = pose(sensors[1]["extrinsics"]) @ np.linalg.inv(pose(sensors[0]["extrinsics"]))
    R, t = T_rl[:3, :3], T_rl[:3, 3]
    if cv is cv2.fisheye:
        R1, R2, P1, P2, _ = cv2.fisheye.stereoRectify(K[0], D[0], K[1], D[1], size, R, t, cv2.CALIB_ZERO_DISPARITY)
        rois = (None, None)
    else:
        R1, R2, P1, P2, _, roi1, roi2 = cv2.stereoRectify(K[0], D[0], K[1], D[1], size, R, t)
        rois = (roi1, roi2)
    maps = [cv.initUndistortRectifyMap(K[i], D[i], (R1, R2)[i], (P1, P2)[i], size, cv2.CV_16SC2) for i in (0, 1)]

    files = [image_files(args.data, left), image_files(args.data, right)]
    if len(files[0]) != len(files[1]):
        print(f"{left} has {len(files[0])} images and {right} {len(files[1])}; pairing by order up to the shorter.",
              file=sys.stderr)
    if args.out:
        os.makedirs(args.out, exist_ok=True)
    for i, pair in enumerate(zip(*files)):
        images = []
        for file, m, roi in zip(pair, maps, rois):
            img = cv2.remap(cv2.imread(file), *m, cv2.INTER_LINEAR)
            if roi is not None and roi[2] > 0:
                img = img[:, roi[0]:roi[0] + roi[2]]
            images.append(img)
        both = np.hstack(images)
        for y in range(0, both.shape[0], max(1, both.shape[0] // 10)):
            cv2.line(both, (0, y), (both.shape[1], y), (0, 255, 0), 1)
        if args.out:
            cv2.imwrite(os.path.join(args.out, f"{i:06d}.png"), both)
        if not args.no_show:
            cv2.imshow(f"{left} | {right}  (any key: next, q: quit)", both)
            if cv2.waitKey(0) & 0xFF in (27, ord("q")):
                break
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
