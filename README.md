# camcalib
### Camera calibration made easy

The latest version is available [here](https://github.com/IVISO/camcalib/releases).

You can purchase a license [here](https://www.camcalib.io/plans-pricing).

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

The extrinsics of a sensor $`S_i`$ is an SE(3) Pose $`P_{S_i E}`$ represented as axis-angle and translation.
$`P_{S_i E}`$ transforms from frame $`E`$ to frame $`S_i`$ where $`E`$ is the reference frame and $`S_i`$ is the frame
of sensor $`i`$.  
Thus the transformation from Sensor $`S_0`$ to $`S_1`$ is given by
```math
P_{S_1 S_0} = P_{S_1 E} * P_{S_0 E}^{-1}
```
#### Note:
Most of the time, the reference frame $`E`$ coincides with the frame of a sensor e.g. $`S_0`$ (called primary).
Then the extrinsics of this sensor is the identity and the transformation of any other sensor frame $`S_0`$ to $`S_i`$ is simply the extrinsics given for $`S_i`$.
```math
P_{S_i S_0} = P_{S_i E}
```
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
