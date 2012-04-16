================================
Writing Extraction Line Scripts
================================

::

	def main():
	    open('A')
	    sleep(1)
	    close('A')
	    
	    info('this is an info message')
	    
	    acquire('pipette')
	    info('loading air shot')
	    open('X')
	    sleep(15)
	    close('X')
	    release('pipette')
	    
--------------------------	    
extraction line functions
--------------------------

.. py:function:: open(alias)
	
	open the valve named ``alias`` e.g ``open('A')``
	
.. py:function:: close(alias)

	open the valve named ``alias`` e.g ``close('A')``


