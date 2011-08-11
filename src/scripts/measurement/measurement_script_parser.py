#============= enthought library imports =======================
#from traits.api import HasTraits, on_trait_change, Str, Int, Float, Button
#from traitsui.api import View, Item, Group, HGroup, VGroup
#============= standard library imports ========================


#============= local library imports  ==========================
from src.scripts.core.core_script_parser import CoreScriptParser
class MeasurementScriptParser(CoreScriptParser):
    COMMAND_KEYS = ['MEASURE']
    def _measure_parse(self, linenum, **kw):
        error = None
        lexer = self._lexer
        token = lexer.get_token()
        mass, settle, peak, baseline = token.split(',')
        #print mass, settle, peak

#        kw['settle'] = float(settle)
#        kw['mass'] = float(mass)
#        kw['peak_center'] = True if peak in ['True', 'true', 'T', 't'] else False
#        peak = True if peak in ['True', 'true', 'T', 't'] else False

        return error, float(mass), float(settle), self._to_bool(peak), self._to_bool(baseline)
#============= EOF =============================================
