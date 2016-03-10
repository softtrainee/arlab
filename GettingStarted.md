## Install Dependencies ##
Note moved to Mercurial version control. TODO: update wiki where appropriate
  1. **Mercurial (hg)** content management system
    * home page: http://mercurial.selenic.com/
  1. **Subversion (SVN)** content management system
    * home page: http://subversion.apache.org/
    * download:  http://subversion.apache.org/packages.html (I suggest using the [CollabNet](http://www.open.collab.net/downloads/subversion/) build; _requires free registration_)
  1. **Enthought Python Distribution (EPD)**
    * home page: http://www.enthought.com/products/epd.php
    * download:  http://www.enthought.com/products/getepd.php
  1. **pyserial**
    * **_required for hardware communication_**
    * home page: http://pyserial.sourceforge.net/
> > install from Cheese Shop using `easy_install`
```
$ sudo easy_install pyserial
```
  1. **opencv**
    * **_required for video_**
    * home page: http://opencv.willowgarage.com/wiki/
    * download:  http://opencv.willowgarage.com/wiki/InstallGuide
  1. **ctypes\_opencv**
    * **_required for video_**
    * home page: http://code.google.com/p/ctypes-opencv/
    * download:  http://code.google.com/p/ctypes-opencv/downloads/list
> > build from src using `setuptools`
```
$ cd path/to/src
$ sudo python setup.py install
```

## Getting the Source ##


**Option 1.** Download and extract a tag. Tags are snapshots of the code at specific times. See [Downloads](http://code.google.com/p/arlab/downloads/list) for available tags.

**Option 2. New** check out beta code using mercurial

```
$ hg clone https://code.google.com/p/arlab/ 
```

**Option 2.** check out beta code
```
$ svn checkout http://arlab.googlecode.com/svn/branches/pychron_beta pychron_beta 
```
**Option 3.** check out stable code
```
$ svn checkout http://arlab.googlecode.com/svn/trunk pychron
```

If you have already checked out a working copy of the source and want to update it to the latest version use
```
$ cd path/to/working_copy
$ svn update
```
See [Source](http://code.google.com/p/arlab/source/checkout) for more info on getting or viewing source code

## Launching ##
From the command line use
```
$ cd path/to/pychron
$ python pychron.py 
```
or if your running the beta version
```
$ cd path/to/pychron_beta
$ python pychron_beta.py 
```

On the first launch pychron will build a Pychrondata directory in the users home folder:

`/Users/[user]` (Mac0S X)

or

`C:\Documents and Settings\[user]\My Documents` (Windows)

### optional for developement ###
  1. **Eclipse**
    * home page: http://www.eclipse.org
    * download:  http://www.eclipse.org/downloads

Use the Eclipse update manager to install Pydev and Subclipse (Help>Install New Software)
  1. **Pydev**
    * home page: http://pydev.org/
    * site: http://pydev.org/updates

Note moved to Mercurial version control. TODO: update wiki where appropriate

  1. **Subclipse**
    * home page: http://subclipse.tigris.org/
    * download:  http://subclipse.tigris.org/servlets/ProjectProcess;jsessionid=712A44119CFE1DD15B53C685143EB4C6?pageID=p4wYuA
Make sure to install the correct [JavaHL](http://subclipse.tigris.org/wiki/JavaHL)