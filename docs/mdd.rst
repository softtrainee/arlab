=========================================
MDD Code and Pychron Basic Documentation
=========================================

This sections provides information on how to model a K-feldspar using Oscar Lovera's
Multiple Diffusion Domain modeling codes. Pychron provides an easy to use GUI to model and
visualize step heating and diffusion data. Currently Pychron simply wraps Lovera's 
fortran codes with a python GUI and does not do any MDD computations.

This documentation uses Oscar Lovera’s most recent (Summer 2012) MDD fortran codes. These have been edited slightly by Clark Short for compatibility with Clark’s / Pychron’s file folder structure and compiled to run on Intel Macs. Use of this guide requires basic command line proficiency.

.. toctree::
	:maxdepth: 1
	Overview
    Outstanding Issues
    MDD Code Compilation
    Data Export from NMGRL Database
    Parsing Autoupdate Files into MDD Files
    Producing Models
    Viewing Data with Pychron
    Pychron Documentation
    Finding Software
    
    
Overview
--------------------------------------------

Dr. Lovera has produced several programs for the manipulation of MDD-spectrum
data. Entries in this list are Fortran_Source_Name.f – “compiled name” format,
where the fortran source name is the name given by Oscar to the source code and
the compiled name is the name given by me to the executable produced during
compilation. To run any of these programs, a SAMPLE.IN file must be created. It
is easiest to do this by taking data from the database via Mass Spec and parsing
the raw data into a SAMPLE.IN file with Pychron. This can also be done with the
Argon macros in Excel with the “Make Sun Files” command, but Pychron is much
less finicky and handles erroneous points (e.g. negative ages) for you.

Many of these files have the capability to run many models in a row in an
automated fashion. This required all of the SAMPLE.IN files to be kept in one
folder. Then, all subsequent files were kept in that folder. It’s a mess, so I
gave each sample its own folder where all of its related files are kept. Its
much better organized, but has limited the mass modeling capabilities of the
original codes. If you want to model several samples at once, I suggest starting
all models simultaneously in separate terminal tabs instead of doing them
sequentially. This is especially powerful on multicore processors, which most
(all?) modern computers have. A single model cannot use more than 1 core.
Therefore, you can run as many models as you have cores without any decrease in
speed. Even when you’re running more models than cores, Argonlab1 cruises.

Dr. Lovera has produced his own documentation, which should be attached to this
document. It is extremely helpful for determining required input files, content
of output files, and resolving a few naming convention issues. The sample files
included with his software are the best way to figure out formatting issues.
Therefore, much of that information will not be re-stated in this document.

Required software: Mass Spec, MDD codes, Pychron, Terminal, Ifort Fortran Compiler

    #. Mddfiles_lst.f – “files”
        Breaks SAMPLE.in into several smaller files used by the different programs. Calculates a preliminary set of kinetic parameters.
        Always the first program you need to run before any other MDD codes.
        Runs instanteously.
        Dialog::
            
            Would you like to read samples from a list? >>	No
            Enter sample name >>	This is usually runID, e.g. 59702-43
            Do you want to exclude some points from E calculation? >>	Up to you. Probably not.
            Enter Sample name (stop to exit) >>	Stop. I use a different file format
    
    #. Autoarr.f – “autoarr”
        Allows you to calculate or dictate kinetic parameters for the sample.
        Dialog for non-automated parameter selection::
        
            Number of max domains >>
            Number of min domains >>
            Keep Do fixed? >>	Yes. should be your default answer
            Activation energy in Kcal/mol >>
            Ordinate of Arrhenius plot >>
            Max plateau of Log(R/Ro) >>
    
    #. Autoage-mon.f – “autoagemon”
        Calculates cooling histories. Assumes monotonic cooling.
        Prints the current run number so you’re aware of progress.
        Dialog::
        
            Insert number of runs. >>	50 is typical, more is better. Max 399.
            Insert max plateau age >>
    
    #. Autoage-free.f – “autoagefree”
        Calculates cooling histories. Allows reheating events.
        Dialog::
        
            Insert number of runs. >>	100 is typical, more is better. Max 399.
            Insert max plateau age >>
            Create contour matrices? >>	Always say yes.
            Insert minimum age
    
    #. Arrme.f – “arrme”
    
    #. Conf_int.f “confint”
        Calculates confidence intervals of cooling histories.
    
    #. Corrfft.f – “corrfft”
        Calculates correlation between LogR/Ro and Arrhenius plots
    
    #. Agesme.f – “agesme”
        Calculates a model spectrum from known kinetics, DD dimensions, and heating schedule.

Outstanding Issues
--------------------------------------------
Oscar used Compaq Visual Fortran (CVF) to compile his codes for 15 years. It's
unique in that it makes a few assumptions that other compilers don't make; we
only snag on one of these differences. Due to an issue with uninitialized
variables we have been unable to compile these on Intel Macs for several years.
In CVF, any uninitialized value is set to 0 (and only usually, and only by
coincidence).

Each program contains several uninitialized values, which influence each program
differently. Instead of digging through 60,000 lines of code to find all
uninitialized variables, you can use the '-save' compiler flag (in Ifort) to
emulate that same auto-zero behavior that Compaq's compiler uses. There are
other potential compatibility issues too, but they haven't come up yet.

Here's a pretty good link for more information on these issues:
`Migrating from Compaq Visual Fortran <http://software.intel.com/en-us/articles/migrating-from-compaq-visual-fortran/>`_

I used the Intel fortran compiler because (1) it should be faster (2) can
automatically optimize a code for the machine it's compiled on, if we want to
try that, and (3) has better documentation than the GNU compiler. I don't know
if gfortran has a similar flag, and if so, what it is.

MDD Code Compilation
--------------------------------------------
Tested on Windows 7, PPC Mac (10.5), and Intel Mac (10.6/10.7)

    #. Install Ifort (Intel’s Fortran Compiler). You can get a trial from their website.
    #. Save the fortran (.f) files in a folder somewhere. You can move it later, but keep them together.
    #. Open the terminal and navigate to the folder containing Lovera’s codes
    #. Compile each individually
        On Mac, type “Ifort PROGRAM.f EXECUTABLE –save”
            Example “Ifort autoage-mon.f autoagemon –save”
        On windows, replace “-save” with “/qsave”
        PROGRAM.f is the name of the file you want to compile
        EXECUTABLE is the name of the executable file, ie what you type into the console to run that program.
    #. Repeat for each program
    #. Add the location of the folder containing your compiled codes to your command line PATH.
    #. Now you’re ready to model some spectra
    
Data Export from NMGRL Database
--------------------------------------------
Exporting data from the database is easy with Mass Spec. I suggest saving autoupdate files to the Modeling folder in the Pychron tree (user/programming/pychrondata_beta/data/modeling/)

    #. Open Mass Spec.
    #. Hit Command-U to open up the autoupdate dialog box.
    #. Uncheck all boxes. Make sure Write / Export drop box is set to “Full raw data”.
    #. Click OK. Save dialog should pop up. Save it however you want.
    #. Add the analyses of interest to the “Selected Runs” box. Do not use markers.
    #. Hit OK. Now your list should be where ever you saved it.
    #. To get the raw data in a MDD-code compatible format, use Pychron.

Parsing Autoupdate Files into MDD Files
--------------------------------------------
In the past this has been done with Excel, but Pychron’s autoupdate handling is faster, easier, and less quirky. Autoupdate parsing in Pychron removes negative ages, causing less snags during modeling. It can handle an autoupdate containing several spectra. It gives each sample its own folder (named with the sample name) and containing a SAMPLE.IN file, which is compatible with my modified MDD programs.
This step requires proper installation and configuration of Pychron, covered in A LATER SECTION.

    #. Open Pychron
    #. CONTINUE

Producing Models
--------------------------------------------
All MDD modeling codes should be run from the command line, although Pychron GUI support is in the works. TO BE CONTINUED.

Viewing Data with Pychron
--------------------------------------------
Evaluation of data and production of graphs is best performed in Pychron. It is
capable of displaying the major MDD plots, including spectra, Arrhenius plots,
Log(r/ro), unconstrained and constrained thermal history models.

Make sure the MDD Perspective is enabled. If your window isn’t similar to
FIGURE, you may be in the Hardware Perspective. Several windows are available
here to aid in data reduction (FIGURE). These windows can be reorganized simply
by dragging them around the window. Therefore, your MDD perspective may not look
exactly like this but it should have all of the same components, although they
may be redistributed.

	A. The Data Window (Far Left)
		The Data window contains a refresh button, which refreshes the graphs. Below
		that is a list of samples. Each sample has a series of check boxes and color
		indicators. “Show” toggles all of the data for that sample on the graphs. “Bind”
		forces the primary and secondary colors to be the same in all plot windows for
		that particular sample. “Ms” toggles the model spectrum produced by Agesme.
		“IMs” toggles the model spectra produced by thermal history modeling. “Ma”
		toggles the model Arrhenius and Log(r/ro) plots. Sometimes the Refresh button
		must be used to display those changes. All samples on this list will be shown in
		the Modeler window.

		Five small buttons are on the upper right corner of this window which (left to
		right) (a) disable column sorting, (b and c) move samples up or down the list,
		which changes their stacking order in the Modeler window, (d) removes a sample
		from the list and (e) opens a preferences window.
		
		Below the list of displayed samples is a navigation window. Simply clicking on a
		sample folder will add it to the list above.

	B. The Summary Window (Top Center)
		The Summary window displays the kinetic parameters and domain distribution for
		the sample highlighted in the Data Window.
	
	C. The Notes Window (Bottom Center)
		The Notes window is basically just a data entry window for a text file. Each
		sample folder has a Notes.txt file which is editable in this window. Any
		information regarding that sample can be saved to that text file and recalled
		simply by click the name of the sample in the Data window. Useful for keeping
		track of why you chose certain kinetic parameters, why the sample is important,
		or any other information you would like to be able to recall later.
	
	D. The Modeler Window (Far Right)	
		The Modeler window displays the samples selected in the Data window.

Pychron Documentation
--------------------------------------------


Finding Software
--------------------------------------------