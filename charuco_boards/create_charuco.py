#!/usr/bin/env python3
"""Draw a ChArUco board for camcalib as a PNG at print scale.

    python create_charuco.py --columns 5 --rows 7 --square-size 0.0375 --marker-size 0.0275 --dictionary C6x6 --page A4 -o charuco_a4.png

The dictionary names are camcalib's marker_type names: C4x4, C5x5, C6x6 and C7x7 (ArUco,
1000 ids each) and A16h5, A25h9, A36h10 and A36h11 (AprilTag). With --page the board is
centred on a white page of that size; without it the PNG is the board alone. The PNG carries
its resolution, so printing it at 100 % gives the board at scale. Measure a square and a marker
after printing and enter them as square_size and marker_size.

camcalib settings for the board: type CharucoBoard, columns, rows, square_size, marker_size and
marker_type as given here (the script prints them).
"""
import argparse
import sys

import cv2
import numpy as np
from PIL import Image

DICTIONARIES = {
    "C4x4": cv2.aruco.DICT_4X4_1000,
    "C5x5": cv2.aruco.DICT_5X5_1000,
    "C6x6": cv2.aruco.DICT_6X6_1000,
    "C7x7": cv2.aruco.DICT_7X7_1000,
    "A16h5": cv2.aruco.DICT_APRILTAG_16h5,
    "A25h9": cv2.aruco.DICT_APRILTAG_25h9,
    "A36h10": cv2.aruco.DICT_APRILTAG_36h10,
    "A36h11": cv2.aruco.DICT_APRILTAG_36h11,
}
PAGES_MM = {"A0": (841, 1189), "A1": (594, 841), "A2": (420, 594), "A3": (297, 420), "A4": (210, 297)}


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--columns", type=int, default=5, help="squares across (default 5)")
    ap.add_argument("--rows", type=int, default=7, help="squares down (default 7)")
    ap.add_argument("--square-size", type=float, default=0.0375, help="side of one square in metres (default 0.0375)")
    ap.add_argument("--marker-size", type=float, default=0.0275, help="side of one marker in metres (default 0.0275)")
    ap.add_argument("--dictionary", choices=list(DICTIONARIES), default="C6x6", help="marker dictionary (default C6x6)")
    ap.add_argument("--page", choices=sorted(PAGES_MM), help="centre the board on a page of this size (portrait)")
    ap.add_argument("--landscape", action="store_true", help="with --page: landscape orientation")
    ap.add_argument("--dpi", type=int, default=200, help="print resolution of the PNG (default 200)")
    ap.add_argument("--output", "-o", default="charuco.png")
    args = ap.parse_args()
    if args.marker_size >= args.square_size:
        sys.exit("The marker must be smaller than the square.")

    px_per_m = args.dpi / 0.0254
    dictionary = cv2.aruco.getPredefinedDictionary(DICTIONARIES[args.dictionary])
    board = cv2.aruco.CharucoBoard((args.columns, args.rows), args.square_size, args.marker_size, dictionary)
    square_px = round(args.square_size * px_per_m)
    image = board.generateImage((args.columns * square_px, args.rows * square_px), marginSize=0, borderBits=1)

    if args.page:
        page_mm = PAGES_MM[args.page]
        if args.landscape:
            page_mm = page_mm[::-1]
        page_px = tuple(round(mm / 1000 * px_per_m) for mm in page_mm)
        if image.shape[1] > page_px[0] or image.shape[0] > page_px[1]:
            sys.exit(f"The board ({image.shape[1] / px_per_m * 1000:.0f} x {image.shape[0] / px_per_m * 1000:.0f} mm) "
                     f"does not fit on {args.page} ({page_mm[0]} x {page_mm[1]} mm).")
        page = np.full((page_px[1], page_px[0]), 255, dtype=np.uint8)
        x = (page_px[0] - image.shape[1]) // 2
        y = (page_px[1] - image.shape[0]) // 2
        page[y:y + image.shape[0], x:x + image.shape[1]] = image
        image = page

    Image.fromarray(image).save(args.output, dpi=(args.dpi, args.dpi))
    height, width = image.shape
    print(f"{args.output}: {width} x {height} px, {width / px_per_m * 1000:.0f} x {height / px_per_m * 1000:.0f} mm at {args.dpi} dpi")
    print("camcalib target settings:")
    print(f"  type: CharucoBoard, columns: {args.columns}, rows: {args.rows}, square_size: {args.square_size}, "
          f"marker_size: {args.marker_size}, marker_type: {args.dictionary}")


if __name__ == "__main__":
    main()
