============== 
Introduction 
==============

Qtegra is a flexible software plaftorm that can be configured in multiple ways
depending on your requirements. Third-party hardware, such as general purpose
actuators, can be directly controlled using a Pericon unit. Qtegra can also be
configured to control third-party hardware indirectly using the TCP or UDP
Internet Protocols. Lastly Qtegra can be configured simply as firmware for the
mass spectrometer. Third-party software clients can then control the mass
spectrometer using a defined ASCII interface.

These three modes are outlined in the following sections. Controlling Qtegra
from a third-party client requires some basic knowledge of network programming.
For a simple networking introduction using Python see the `socket
<http://docs.python.org/library/socket.html>`_ module and `examples
<http://docs.python.org/library/socket.html#example>`_.

Qtegra can be highly customized by using `C-sharp
<http://en.wikipedia.org/wiki/C_Sharp_%28programming_language%29>`_ scripts. `C#
Language and the .NET Framework <http://msdn.microsoft.com/library/z1zx9t92>`_
is a very helpful reference

.. figure:: figure1.pdf
	:scale: 50 %
	
	caption figure 1