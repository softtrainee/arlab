=========================
Mass Spec Run Scripts
=========================

This section describes how to write Mass Spec Run Scripts inconjuction with Pychron

===================== ===========================================
Command				  Arguments				
===================== ===========================================
DeviceErrorHandler    ``errorCode`` ``handler``
DeviceRead			  ``deviceName`` ``command`` ``userVariable``
DeviceWait			  ``deviceName`` ``command`` ``comp`` ``criterion``
DeviceWrite			  ``deviceName`` ``command``
===================== ===========================================


.. describe:: DeviceErrorHandler
	
::
	
	DeviceErrorHandler "101" "PumpAndQuit"

.. describe:: DeviceRead
	
::
	
	DeviceRead "Pychron Extr Microcontroller" "Read boneEquilTime" "boneEquil"

**Note:**
	In *Read name*, ``name`` can refer to Devices, Flags, TimedFlags, or parameters defined in ``mass_spec_params.cfg``

.. describe:: DeviceWait
	
::
	
	DeviceWait "Pychron Extr Microcontroller" "GetFlag PipetteAccess" "=" "0"

A **DeviceWait** command should be read as, "Wait until the PipetteAccess flag equals zero". By default, waiting times out after 10000 seconds
	
.. describe:: DeviceWrite
	
::
	
	DeviceWrite "Pychron Extr Microcontroller" "SetTimedFlag CO2PumpTime"	
	
This command can be used to send raw command strings to the device.