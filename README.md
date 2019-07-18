# Search-And-Sample-Return
Udacity Robotics Nanodegree - Term I - Rover Project 


Project: Search and Sample Return
The goals / steps of this project are the following:
Training / Calibration:
a. Download the simulator and take data in "Training Mode"

b. Test out the functions in the Jupyter Notebook provided

c. Add functions to detect obstacles and samples of interest (golden rocks)

d. Fill in the `process_image()` function with the appropriate image processing steps (perspective
transform, color threshold etc.) to get from raw images to a map. The `output_image` you create
in this step should demonstrate that your mapping pipeline works.

e. Use `moviepy` to process the images in your saved dataset with the `process_image()` function.
Include the video you produce as part of your submission.


Autonomous Navigation / Mapping

a. Fill in the `perception_step()` function within the `perception.py` script with the appropriate
image processing functions to create a map and update `Rover()` data (similar to what you did
with `process_image()` in the notebook).

b. Fill in the `decision_step()` function within the `decision.py` script with conditional statements
that take into consideration the outputs of the `perception_step()` in deciding how to issue
throttle, brake and steering commands.

c. Iterate on your perception and decision function until your rover does a reasonable (need to
define metric) job of navigating and mapping.
