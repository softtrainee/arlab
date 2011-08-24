'''
Device Creator File
'''
#============= enthought library imports =======================

#============= standard library imports ========================

#============= local library imports  ==========================
from src.hardware.core.core_device import CoreDevice
class FerrupsUPS(CoreDevice):

	scan_func = None
	def __init__(self,*args,**kw):
		super(FerrupsUPS,self).__init__(*args,**kw)

	def load_additional_args(self,config):
		return True

	def _parse_response(self,resp):
		if self.simulation:
		    resp = self.get_random_value(0,10)
		elif resp is not None:
		    resp = resp.strip()
		return resp

	def _build_command(self,cmd):
		return cmd

	def _build_query(self,qry):
		return qry

	def get_status(self):
		qry = 'status'
		qry = self._build_query(qry)
		resp = self.ask(qry)
		return self._parse_response(resp)

	def get_ambient_temperature(self):
		qry = 'ambtemp'
		qry = self._build_query(qry)
		resp = self.ask(qry)
		return self._parse_response(resp)


#============ EOF ==============================================
