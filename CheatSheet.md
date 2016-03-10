# Plugins #
  * Enable Plugins in Menu > Tools > Preferences > Plugins
  * Plugins grouped by category General, Hardware, Data
  * ~~Enable UI Plugin with Plugin~~ UI plugin automatically included
  * see plugin file Pychrondata/plugins/plugins.xml

## Hardware Plugins ##
### Extraction Line ###
  * **Actuating Valves**
The valves on the extraction line can be actuated i.e. opened or closed using the extraction line canvas. Each sphere represents a valve. The color of the sphere indicates the valves state: red = closed, green = open. The valves can be locked from user interaction. Locking a valve prevents both Pychron and any device talking to Pychron from actuating the valve. To lock right click on the valve. A blue spherical cage encloses locked valves. Right click to unlock.
To get information about a valve hover over the sphere and hit 'Ctrl'. A information dialog will popup showing the valve name, state and locked state, all information that is already visually encoded.

  * **Manupulating the 3D Canvas**
To add User defined view and keybinding

For example define a home view and activate by pressing 'h'

  1. Menu > Extraction Line > Canvas Views
  1. Use buttons in the toolbar (upper right) to added and delete User Views.
  1. Use sliders to adjust view
  1. User color dialog to change background color

Rotation of the Extraction Line model in 3D is accomplished using a [virtual arcball](http://www.cabiatl.com/mricro/obsolete/graphics/3d.html). Hold down the left mouse button in a empty area of the canvas and drag the mouse in the direction of rotation.

### CO2 Laser ###
  * **CO2 laser shot**
    1. Open laser manager
      * Menu > Laser > Laser Manager
    1. Move to sample hole
      * see MoveLaser
    1. Focus Camera
      * Use Zoom slider to zoom camera
      * Use the Z slider to focus camera.
      * Camera and Laser have the same focal plane
    1. Set Beam Diameter
      * Use the beam slider to set the beam diameter.
      * Nominal value for fusing a FC-2 crystal is 1.0
    1. Enable Laser
      * Click Enable button
      * If enabled LED set to Green
    1. Set Laser Power
      * Set the laser power in % of total power.
      * Acceptable values 0-100.
      * Nominal power for fusing a FC-2 crystal is 5.0-10.0% at 1.0 beam diameter
    1. Stop Lasing
      * Click Stop button
      * Sets laser power to 0.0 and disables the laser
      * LED set to Red


### Diode Laser ###
