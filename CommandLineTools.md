#Command line tools help page

# Command Line Tools #
  * installer.py
  * device\_creator.py

## installer.py ##
```
usage: installer.py [-h] [prefix] [name]

Create a new Launchable Application

positional arguments:
  prefix      Prefix name. used to identify the icon file and the launch
              script eg. pychron
  name        Name of the application bundle eg. Pychron

optional arguments:
  -h, --help  show this help message and exit
```
## hardware\_creator.py ##
```
usage: hardware_creator.py [-h] [-o [file_name]] [-i [input file_name]]
                           [class_name]

Create a new hardware device

positional arguments:
  class_name            camel case class name

optional arguments:
  -h, --help            show this help message and exit
  -o [file_name]        Python file name for the hardware
  -i [input file_name]  XML input file
```