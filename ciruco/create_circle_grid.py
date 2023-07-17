#!/usr/bin/env python
import argparse
from svgfig import *
from aruco_marker import *


class PatternMaker:
    def __init__(self, cols, rows, output, units, square_size, radius_rate, page_width, page_height):
        self.cols = cols
        self.rows = rows
        self.output = output
        self.units = units
        self.square_size = square_size
        self.radius_rate = radius_rate
        self.width = page_width
        self.height = page_height
        self.g = SVG("g")  # the svg group container

    def make_circles_pattern(self, aruco=True):
        spacing = self.square_size
        r = spacing / self.radius_rate
        pattern_width = ((self.cols - 1.0) * spacing) + (2.0 * r)
        pattern_height = ((self.rows - 1.0) * spacing) + (2.0 * r)
        if self.width is None or self.height is None:
            self.width = pattern_width
            self.height = pattern_height
        x_spacing = (self.width - pattern_width) / 2.0
        y_spacing = (self.height - pattern_height) / 2.0
        for x in range(0, self.cols):
            for y in range(0, self.rows):
                dot = SVG("circle", cx=(x * spacing) + x_spacing + r,
                          cy=(y * spacing) + y_spacing + r, r=r, fill="black", stroke="none")
                self.g.append(dot)

        x = x_spacing + 2 * self.square_size / self.radius_rate
        ss = self.square_size - 2 * self.square_size / self.radius_rate
        for j in range(self.cols - 1):
            y = y_spacing + 2 * self.square_size / self.radius_rate
            for i in range(self.rows - 1):
                aruco: SVG = get_aruco_marker("DICT_6X6_1000", j + i * (self.cols - 1), ss, 1, x=x, y=y)
                self.g.append(aruco)
                y += self.square_size
            x += self.square_size

    def make_acircles_pattern(self, aruco=True):
        spacing = self.square_size
        r = spacing / self.radius_rate
        pattern_width = ((self.cols-1.0) * 2 * spacing) + spacing + (2.0 * r)
        pattern_height = ((self.rows-1.0) * spacing) + (2.0 * r)
        if self.width is None or self.height is None:
            self.width = pattern_width
            self.height = pattern_height
        x_spacing = (self.width - pattern_width) / 2.0
        y_spacing = (self.height - pattern_height) / 2.0
        for x in range(0, self.cols):
            for y in range(0, self.rows):
                dot = SVG("circle", cx=(2 * x * spacing) + (y % 2)*spacing + x_spacing + r,
                          cy=(y * spacing) + y_spacing + r, r=r, fill="black", stroke="none")
                self.g.append(dot)

        x = x_spacing + 2 * self.square_size - self.square_size / 2 + r
        ss = self.square_size
        for j in range(self.cols - 1):
            y = y_spacing + 0.5 * self.square_size + r
            for i in range(self.rows - 1):
                aruco: SVG = get_aruco_marker("DICT_6X6_1000", j + i * (self.cols - 1), ss, 1, x=x, y=y)
                self.g.append(aruco)
                y += self.square_size * 2
            x += self.square_size * 2

    def make_checkerboard_pattern(self):
        spacing = self.square_size
        xspacing = (self.width - self.cols * self.square_size) / 2.0
        yspacing = (self.height - self.rows * self.square_size) / 2.0
        for x in range(0, self.cols):
            for y in range(0, self.rows):
                if x % 2 == y % 2:
                    square = SVG("rect", x=x * spacing + xspacing, y=y * spacing + yspacing, width=spacing,
                                 height=spacing, fill="black", stroke="none")
                    self.g.append(square)

    def save(self):
        c = canvas(self.g, fill="white", width="%d%s" % (self.width, self.units), height="%d%s" % (self.height, self.units),
                   viewBox="0 0 %d %d" % (self.width, self.height))
        open(self.output, "w").write(c.standalone_xml(encoding="utf-8"))
        # c.inkscape(self.output)
        # c.save(self.output)
        # svg2png(bytestring=c.standalone_xml(encoding="utf-8"), write_to="output.png", background_color='white')
        # img = cv2.imread("output.png", cv2.IMREAD_GRAYSCALE)
        # # cv2.imwrite("output.png", img)
        # plt.imshow(img)
        # plt.show()


def get_aruco_marker(dictionary, markerID, markerLength, borderBits=1, pageBorder=(0, 0), x=0, y=0):
    MarkerPrinter.CheckArucoMarkerImage(dictionary, markerID, markerLength, borderBits=borderBits, pageBorder=pageBorder)

    marker = MarkerPrinter.ArucoBits(dictionary, markerID)
    markerSize = marker.shape[0]

    markerBitMap = np.zeros(shape=(markerSize + borderBits * 2, markerSize + borderBits * 2), dtype=bool)
    markerBitMap[borderBits:-borderBits, borderBits:-borderBits] = marker
    # markerBitMap = np.swapaxes(markerBitMap, 0, 1)

    pt = markerLength / len(markerBitMap)
    svgs = SVG("g")
    for i, row in enumerate(markerBitMap):
        for j, cell in enumerate(row):
            if not cell:
                svgs.append(SVG("rect", x=x + j * pt, y=y + i * pt, width=pt, height=pt, fill="black", stroke="None"))
    return svgs

def main():
    # parse command line options
    parser = argparse.ArgumentParser(description="generate camera-calibration pattern", add_help=False)
    parser.add_argument("-H", "--help", help="show help", action="store_true", dest="show_help")
    parser.add_argument("-o", "--output", help="output file", default="out.svg", action="store", dest="output")
    parser.add_argument("-c", "--columns", help="pattern columns", default="8", action="store", dest="columns",
                        type=int)
    parser.add_argument("-r", "--rows", help="pattern rows", default="11", action="store", dest="rows", type=int)
    parser.add_argument("-T", "--type", help="type of pattern", default="circles", action="store", dest="p_type",
                        choices=["circles", "acircles", "checkerboard"])
    parser.add_argument("-u", "--units", help="length unit", default="mm", action="store", dest="units",
                        choices=["mm", "inches", "px", "m"])
    parser.add_argument("-s", "--square_size", help="size of squares in pattern", default="20.0", action="store",
                        dest="square_size", type=float)
    parser.add_argument("-R", "--radius_rate", help="circles_radius = square_size/radius_rate", default="5.0",
                        action="store", dest="radius_rate", type=float)
    parser.add_argument("-w", "--page_width", help="page width in units", default=argparse.SUPPRESS, action="store",
                        dest="page_width", type=float)
    parser.add_argument("-h", "--page_height", help="page height in units", default=argparse.SUPPRESS, action="store",
                        dest="page_height", type=float)
    parser.add_argument("-a", "--page_size", help="page size, superseded if -h and -w are set", default="A4", action="store",
                        dest="page_size", choices=["A0", "A1", "A2", "A3", "A4", "A5"])
    args = parser.parse_args()

    show_help = args.show_help
    if show_help:
        parser.print_help()
        return
    output = args.output
    columns = args.columns
    rows = args.rows
    p_type = args.p_type
    units = args.units
    square_size = args.square_size
    radius_rate = args.radius_rate
    if 'page_width' and 'page_height' in args:
        page_width = args.page_width
        page_height = args.page_height
    else:
        page_size = args.page_size
        # page size dict (ISO standard, mm) for easy lookup. format - size: [width, height]
        page_sizes = {"A0": [840, 1188], "A1": [594, 840], "A2": [420, 594], "A3": [297, 420], "A4": [210, 297],
                      "A5": [148, 210]}
        page_width = page_sizes[page_size][0]
        page_height = page_sizes[page_size][1]
    # pm = PatternMaker(columns, rows, output, units, square_size, radius_rate, page_width, page_height)
    pm = PatternMaker(columns, rows, output, units, square_size, radius_rate, None, None)
    # dict for easy lookup of pattern type
    mp = {"circles": pm.make_circles_pattern, "acircles": pm.make_acircles_pattern,
          "checkerboard": pm.make_checkerboard_pattern}
    mp[p_type]()
    # this should save pattern to output
    pm.save()


if __name__ == "__main__":
    main()