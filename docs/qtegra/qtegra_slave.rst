======================
Qtegra As A Slave
======================


This section describes how to setup **Qtegra As A Slave**. In this configuration
you can think of Qtegra simply as the mass spectrometer's firmware.

Interface with Qtegra
-------------------------
Server
------
	#. Start Server
	#. Accept incoming commands
	#. Parse command
	#. Execute command with Qtegra core
	#. Return response
	
Client
-------
	#. Open connection to Server
	#. Send ASCII command
	#. Read response

Key Concepts
-------------
	#. sockets
	#. TCP and UDP
	#. C-sharp and .NET


Command Set
------------

.. table:: Qtegra Commands

	============= ============= ==============================================================
	Command       Arguments     Description
	============= ============= ==============================================================
	SetParameter  ``param,val`` Set ``param`` to ``val``
	GetParameter  ``param``     Get ``param`` 
	============= ============= ==============================================================

Examples
---------

`````````````````````
Server boilerplate
`````````````````````
.. code-block:: csharp
	
	public void main()
	{
	//start server
	}
	private void start_server()
	{	
	}
	private void parse_command(string cmd)
	{
	}
	
````````````````````````````
Client boilerplate (python) 
````````````````````````````
.. code-block:: python

	import socket
	sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.send('GetParameter Y-symmetry')
	print sock.read()
	