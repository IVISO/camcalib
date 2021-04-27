# camcalib
### Camera calibration made easy

The latest version is available [here](https://github.com/IVISO/camcalib/releases).

You can purchase a license [here](https://www.camcalib.io/plans-pricing).

You can try camcalib 14 days for free. Just open the AppImage and create a demo key.
The calibration results in the demo version are rounded. If you need results with higher precision, you need to buy a license [here](https://www.camcalib.io/plans-pricing).

For more information visit our [website](https://www.camcalib.io/).

If you want to stream data from IDS cameras you need to install the driver from https://en.ids-imaging.com/downloads.html.


### Bugs and features

If you encounter any problems or have a feature request you can check the [issues page](https://github.com/IVISO/camcalib/issues) and open a new issue.


## Documentation

### Calibration Data

If calibration data is loaded from disk, there are currently two ways.
Either the data must be provided as indexed ROS bag or as PNG images structured in folders.
Currently, PNG images are supported.

For the folder method, it is necessary that your images are structured in subfolders.
The names of the subfolders are taken as unique camera ids.

For the **extrinsic calibration** it is necessary that the images are recognised as synchronised.
Therefore, images, that are taken at the exact same time, must have the same filename.
If timestamps are used for the image filename, use "_" as decimal seperator.  
For example:
```
dataset
├── cam0
│   ├── 0_03.png
│   ├── 0_25.png
│   ├──     ...
│   └── 9_76.png
├── cam1
│   ├── 0_03.png
│   ├── 0_25.png
│   ├──     ...
│   └── 9_76.png
│   ...
```

### Calibration board

Currently, [AprilTag](https://github.com/ethz-asl/kalibr/wiki/calibration-targets) and [ChArUco](https://docs.opencv.org/3.4/df/d4a/tutorial_charuco_detection.html) boards are supported. This will change in the future.  
If you have troubles to get one of these, don't hesitate to [contact us](mailto:info@camcalib.io).

### Imu

Please ensure that:

  * accelerometer values are in <img src="https://latex.codecogs.com/gif.latex?\frac{m}{sec^{2}}" />.
  * gyroscope values are in <img src="https://latex.codecogs.com/gif.latex?\frac{rad}{sec}" />.

### Camera Model

Supported camera models are 
- Pinhole (fx, fy, cx, cy):
  * fx, fy: focal length, cx, cy: image center
  * for cameras without distortion
- PinholeRadTan (fx, fy, cx, cy, k1, k2, p1, p2): ([details](https://docs.opencv.org/3.4.12/dc/dbb/tutorial_py_calibration.html))
  * fx, fy: focal length; cx, cy: image center; k1, k2: radial distortion; p1, p2: tangential distortion
  * common model compatible with openCV, matlab, etc.
- DoubleSphere (fx, fy, cx, cy, xi, alpha): ([details](https://arxiv.org/pdf/1807.08957v1.pdf))
  * fx, fy: focal length; cx, cy: image center; xi: sphere shift; alpha: image plane shift
  * works with all kind of lens distortion even with fisheye
  * few distortion parameters (xi, alpha) makes optimization more robust


### Calibration Result

Calibration results can be exported as YAML file.
The parameters can then be found in the "sensors" section.
Depending on the type of calibration, each camera identifier has intrinsic and possibly extrinsic parameters.

The intrinsics section has the keys "type" that specifies the chosen camera model and "parameters" that holds the
calibrated parameters corresponding to the camera model.

The extrinsics of a sensor <img src="https://latex.codecogs.com/gif.latex?S_i" /> is an SE(3) Pose <img src="https://latex.codecogs.com/gif.latex?P_%7BS_i%20E%7D" /> represented as axis-angle and translation.
<img src="https://latex.codecogs.com/gif.latex?P_%7BS_i%20E%7D" /> transforms from frame <img src="https://latex.codecogs.com/gif.latex?E" /> to frame <img src="https://latex.codecogs.com/gif.latex?S_i" /> where <img src="https://latex.codecogs.com/gif.latex?E" /> is the reference frame and <img src="https://latex.codecogs.com/gif.latex?S_i" /> is the frame
of sensor <img src="https://latex.codecogs.com/gif.latex?i" />.  
Thus the transformation from Sensor <img src="https://latex.codecogs.com/gif.latex?S_0" /> to <img src="https://latex.codecogs.com/gif.latex?S_1" /> is given by

![equation](https://latex.codecogs.com/gif.latex?P_%7BS_1%20S_0%7D%20%3D%20P_%7BS_1%20E%7D%20*%20P_%7BS_0%20E%7D%5E%7B-1%7D)

#### Note:
Most of the time, the reference frame <img src="https://latex.codecogs.com/gif.latex?E" /> coincides with the frame of a sensor e.g. <img src="https://latex.codecogs.com/gif.latex?S_0" /> (called primary).
Then the extrinsics of this sensor is the identity and the transformation of any other sensor frame <img src="https://latex.codecogs.com/gif.latex?S_0" /> to <img src="https://latex.codecogs.com/gif.latex?S_i" /> is simply the extrinsics given for <img src="https://latex.codecogs.com/gif.latex?S_i" />.

![equation](https://latex.codecogs.com/gif.latex?P_%7BS_i%20S_0%7D%20%3D%20P_%7BS_i%20E%7D)

An example results file could look like the following:  

```yaml
sensors:
  'cam0':
    extrinsics:
      axis_angle:
      - 0.0
      - 0.0
      - 0.0
      translation:
      - 0.0
      - 0.0
      - 0.0
    intrinsics:
      parameters:
        alpha: 0.30000000000000004
        cx: 640.0
        cy: 510.0
        fx: 2300.0
        fy: 2300.0
        image_size:
        - 1280
        - 1024
        xi: -0.001
      type: DoubleSphereInit
  'cam1':
    extrinsics:
      axis_angle:
      - 0.3000000000000015
      - 0.20000000000000084
      - 0.01999999999999994
      translation:
      - -0.2
      - 0.30000000000000004
      - 0.30000000000000004
    intrinsics:
      parameters:
        alpha: 0.30000000000000004
        cx: 640.0
        cy: 510.0
        fx: 2300.0
        fy: 2300.0
        image_size:
        - 1280
        - 1024
        xi: -0.002
      type: DoubleSphereInit
```
