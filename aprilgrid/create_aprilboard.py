#!/usr/bin/env python3
"""Draw an AprilBoard for camcalib as a PNG at print scale.

    python create_aprilboard.py --columns 6 --rows 6 --tag-size 0.088 --tag-spacing 0.3 --family A36h11 -o aprilboard.png

The layout is the one camcalib's AprilBoard detector expects (the same code as
camcalib.boardgenerator in the camcalib wheel): tags of `tag_size` metres, gaps of
`tag_spacing` times the tag size with a black square at every corner, tag ids counted from
`start_id` row by row. The PNG carries its resolution, so printing it at 100 % gives the board
at scale; measure one tag after printing and enter that as tag_size.

camcalib settings for the board: type AprilBoard, columns, rows, tag_size, tag_spacing and
marker_type as given here (the script prints them).
"""
import argparse

import cv2
import numpy as np
from PIL import Image

FAMILIES = {
    "A16h5": cv2.aruco.DICT_APRILTAG_16h5,
    "A25h9": cv2.aruco.DICT_APRILTAG_25h9,
    "A36h10": cv2.aruco.DICT_APRILTAG_36h10,
    "A36h11": cv2.aruco.DICT_APRILTAG_36h11,
}


def aprilboard(start_id, tag_px, tag_spacing, rows, cols, border, dictionary):
    """The board as an 8-bit image; same layout as camcalib.boardgenerator.generate_aprilboard."""
    aruco_dict = cv2.aruco.getPredefinedDictionary(dictionary)
    spacing_px = int(tag_spacing * tag_px)
    border_px = int(border * tag_px)
    width = int((cols + 1) * spacing_px + cols * tag_px) + 2 * border_px
    height = int((rows + 1) * spacing_px + rows * tag_px) + 2 * border_px
    board = np.full((height, width), 255, dtype=np.uint8)
    for row in range(rows):
        for col in range(cols):
            tag_id = start_id + row * cols + col
            x = (cols - col - 1) * (tag_px + spacing_px) + spacing_px + border_px
            y = row * (tag_px + spacing_px) + spacing_px + border_px
            board[y:y + tag_px, x:x + tag_px] = aruco_dict.generateImageMarker(tag_id, tag_px, borderBits=2)
    for row in range(rows + 1):
        for col in range(cols + 1):
            x = col * (tag_px + spacing_px) + border_px
            y = row * (tag_px + spacing_px) + border_px
            board[y:y + spacing_px, x:x + spacing_px] = 0
    return board


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--columns", type=int, default=6, help="tags across (default 6)")
    ap.add_argument("--rows", type=int, default=6, help="tags down (default 6)")
    ap.add_argument("--tag-size", type=float, default=0.088, help="side of one tag in metres (default 0.088)")
    ap.add_argument("--tag-spacing", type=float, default=0.3, help="gap between tags as a fraction of the tag size (default 0.3)")
    ap.add_argument("--family", choices=sorted(FAMILIES), default="A36h11", help="AprilTag family (default A36h11)")
    ap.add_argument("--start-id", type=int, default=0, help="id of the first tag (default 0); a second board of the same size starts at columns*rows")
    ap.add_argument("--border", type=float, help="white margin as a fraction of the tag size (default: the tag spacing)")
    ap.add_argument("--dpi", type=int, default=200, help="print resolution of the PNG (default 200)")
    ap.add_argument("--output", "-o", default="aprilboard.png")
    args = ap.parse_args()

    px_per_m = args.dpi / 0.0254
    tag_px = round(args.tag_size * px_per_m)
    border = args.tag_spacing if args.border is None else args.border
    board = aprilboard(args.start_id, tag_px, args.tag_spacing, args.rows, args.columns, border, FAMILIES[args.family])
    Image.fromarray(board).save(args.output, dpi=(args.dpi, args.dpi))

    height, width = board.shape
    print(f"{args.output}: {width} x {height} px, {width / px_per_m * 1000:.0f} x {height / px_per_m * 1000:.0f} mm at {args.dpi} dpi")
    print("camcalib target settings:")
    print(f"  type: AprilBoard, columns: {args.columns}, rows: {args.rows}, tag_size: {args.tag_size}, "
          f"tag_spacing: {args.tag_spacing}, marker_type: {args.family}")


if __name__ == "__main__":
    main()
