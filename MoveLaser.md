# Moving the Laser #

## Linear Move ##
Linear moves i.e. x1,y1 to x2,y2, are possible by clicking on the Video Canvas. Moves are trapezoidal and the accel, velocity and decel are calculated on-the-fly to ensure smooth motion.

## Single Axis Move ##
A single axis move, most commonly used to adjust the laser in the Z-axis, is possible using the Z slider in the Laser Manager.

## Calibrate Stage ##
Calibrating the stage enables the use of **Move to Hole**. The calibration routine is the same as Mass Spec:
  1. Start Calibration routine - click Calibrate Stage
  1. Locate Center - move the laser to you desired center. click Locate Center
  1. Locate Right - move the laser in the desired right direction. click Locate Right

The stage calibration is automatically saved to file and loaded when the Laser Manager is opened.
**@TODO currently only one calibration file is available. Add ability to select and load a calibration from file**

## Move to Hole ##
Once the stage has been calibrated select the desired Stage Map from the drop now menu above the Canvas. Enter the Hole # in Hole: and hit Enter.  The laser will make a linear move to the selected hole. **Fine tune adjustment is required once initial linear move is complete, therefore this process currently should not be used for automation.**

## Tricks ##