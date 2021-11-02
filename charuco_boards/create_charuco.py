'''
@author: IVISO GmbH
@date: 02.11.2021
dependencies:
$ pip install opencv-contrib-python reportlab
'''
import cv2
import numpy as np
import reportlab.lib.pagesizes as din

cm_per_inch = 2.54
marker_size = 0.0275
square_size = 0.0375
n_col = 5
n_row = 7
marker_type = "6x6"
page_format = "A4"
dpi = 72

page_size = np.asarray(getattr(din, page_format))
page_size = page_size * dpi / 72
board_size = dpi * np.array([n_col, n_row]) * square_size * 100 / cm_per_inch
assert np.all(board_size < page_size), f"bord does not fit {board_size} < {page_size}"

dictionary = cv2.aruco.getPredefinedDictionary(getattr(cv2.aruco, "DICT_" + marker_type.upper() + "_1000"))
board = cv2.aruco.CharucoBoard_create(n_col, n_row, square_size, marker_size, dictionary)
board_image = board.draw(tuple(board_size.astype(np.int)))
cv2.imwrite(f"charuco_{page_format}_{n_col}x{n_row}_ms={marker_size}_ss{square_size}_dict{marker_type}".replace('.', ',') + ".png", board_image)
