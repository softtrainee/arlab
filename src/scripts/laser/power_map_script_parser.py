#============= enthought library imports =======================
#from traits.api import HasTraits, on_trait_change, Str, Int, Float, Button
#from traitsui.api import View, Item, Group, HGroup, VGroup

#============= standard library imports ========================

#============= local library imports  ==========================
from src.scripts.core.core_script_parser import CoreScriptParser
class PowerMapScriptParser(CoreScriptParser):
    def raw_parse(self, args):
        error = None
        sargs = 'Beam, Padding, StepLength, Power'
        e1 = 'Not enough args ' + sargs
        if len(args) < 4:
            error = e1
        elif len(args) == 4 and not args[3]:
            error = e1
        elif len(args) > 4:
            error = 'Too many args ' + sargs
        else:
            error = self._check_number(args)

        return error, args
#============= views ========



#============= views ===================================
#============= EOF ====================================
