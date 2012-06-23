========================
Building MDD Fortran 
========================


​Tested on Windows 7, PPC Mac (10.5), and Intel Mac (10.6/10.7)
 
 
Before trying to compile your own binaries, try using the ones packages with the pychron source. 
They are located in ~/Programming/mercurial/pychron/src/modeling/lovera/bin

Compile for Mac OSX
---------------------
	#. Install Xcode.
		a. Download from `Apple Developer Center <https://developer.apple.com/xcode/>`_
		
		b. Although Xcode is free, you must have an Apple account which requires a credit card number.

	#. Install Ifort (Intel Fortran Composer). You can get a trial from their website, but it only lasts a month so don’t waste it, or you can buy the academic license for ~$280.
		a. Download Ifort (`link <http://google.com>`_)
		
		b. Register with Intel (`link <https://registrationcenter.intel.com/RegCenter/AutoGen.aspx?ProductID=1524&AccountID=&EmailID=&ProgramID=&RequestDt=&rm=EVAL&lang= .>`_)
		
		c. During installation, it will ask if you want to perform a Command line install, or xcode integration environment, or both – select both.
	
	#. Open Terminal and navigate to Pychron's Lovera directory::
	
		$ cd ~/Programming/mercurial/pychron/src/modeling/lovera
		
	#. Compile source code.
		a. Pychron provides a bash script to automate the building of the mdd
		   codes. It is located in the Pychron Lovera directory. ::
			
			$ ./build.py 	
			
		b. **Or**, compile manually use ``Ifort PROGRAM.f EXECUTABLE –save`` ::
			
			$ Ifort autoage-mon.f autoagemon –save

		PROGRAM.f is the name of the file you want to compile
			
		EXECUTABLE is the name of the executable file, ie what you type into the console to run that program.
			
		On windows, replace “-save” with “/qsave”
			
	#. Add the location of the folder containing your compiled codes to your command line ``PATH``.
	
	#. Add the compile codes to the ``PATH`` environment variable::
		
		$ open ~/.profile
		
	This will open the .profile file in a text editor. Add ``export
	PATH=~/Programming/mercurial/pychron/modeling/lovera/bin:$PATH`` to the file. Save and close::
		
		$ source ~/.profile
		
	#. Now you’re ready to model.
	
	#. To use the Pychron integrated modeling codes, you must compile those
	   separately with specific names, i.e files_py, autoarr_py, autoagemon_py,
	   autoagefree_py, confint_py, corrfft_py, agesme_py, and arrme_py.  If you use the build.py script
	   simply enable the pychron flag::
	
		$ ./build.py --pychron 
		
		