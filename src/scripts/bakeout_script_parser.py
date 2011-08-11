#============= enthought library imports =======================

#============= standard library imports ========================

#============= local library imports  ==========================
from src.scripts.core.core_script_parser import CoreScriptParser

class BakeoutScriptParser(CoreScriptParser):

    def raw_parse(self, args):
        error = None
        sargs = 'Setpoint(C), Duration(min)'
        if len(args) < 2 or (len(args) == 2 and not args[1]):
            error = 'Not enough args ' + sargs
        elif len(args) > 2:
            error = 'Too many args ' + sargs
        else:
            #check all are numbers

            error = self._check_number(args)


        return error, args
#============= views ===================================
#============= EOF ====================================
