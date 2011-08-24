'''
Device Creator File
'''
#============= enthought library imports =======================

#============= standard library imports ========================

#============= local library imports  ==========================
from hardware.core.core_device import CoreDevice
class EMON(CoreDevice):

	scan_func = None
	def __init__(self,*args,**kw):
		super(EMON,self).__init__(*args,**kw)

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

	def func(self,f):
		cmd = 'a'
                cmd = self._build_command(cmd,f)
                resp = self.ask(cmd)
                return self._parse_response(resp)


#============ EOF ==============================================
