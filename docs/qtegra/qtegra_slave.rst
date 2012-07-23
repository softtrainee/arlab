======================
Qtegra As A Slave
======================


This section describes how to setup **Qtegra As A Slave**. In this configuration
you can think of Qtegra simply as the mass spectrometer's firmware.

Interface with Qtegra
-------------------------

Key Concepts
-------------

	#. TCP and UDP
	#. C-sharp and .NET


Command Set
------------

============= ============= ==============================================================
Command       Arguments     Description
============= ============= ==============================================================
GetData                     Return csv-list of detector intensities
SetHV         <volts>       Set source accelerating voltage
GetHV                       Set source accelerating voltage
SetDeflection <det>,<volts> Set ``det`` deflection voltage to ``volts``
GetDeflection <det>         Get ``det`` deflection voltage
============= ============= ==============================================================


.. rubric:: Footnotes

.. [#] Data can be returned in a tagged and untagged version. e.g H1:1000,H2:100... or 1000,100. Use the variable ``tag_data`` in RemoteControlServer.cs to control this behavior
