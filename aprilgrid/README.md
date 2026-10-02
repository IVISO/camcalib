# AprilBoard

Two ready-made boards of AprilTag 36h11 tags with 0.088 m tags and a gap of 0.3 times the tag size,
as PDF and EPS: 6 by 6 tags and 12 by 6 tags. Print at 100 % and measure one tag; the camcalib
target settings are then

| setting | value |
|---|---|
| type | AprilBoard |
| columns, rows | the tags you count across and down (6 and 6, or 12 and 6) |
| tag_size | the measured tag side in metres (0.088 when printed at scale) |
| tag_spacing | 0.3 |
| marker_type | A36h11 |

Other sizes: `create_aprilboard.py` draws a board as a PNG at print scale with the layout
camcalib expects, for example

```
python create_aprilboard.py --columns 6 --rows 6 --tag-size 0.088 --tag-spacing 0.3 --family A36h11 -o aprilboard.png
```

It prints the matching camcalib settings. Dependencies: `pip install -r ../requirements.txt`
(OpenCV 4.7 or newer). The camcalib wheel has the same generator as `camcalib.boardgenerator`.
