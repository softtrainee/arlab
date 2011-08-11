#============= enthought library imports =======================
from traits.api import HasTraits, Str, Int, List, Instance
from traitsui.api import View, Item, TableEditor
from traitsui.table_column import ObjectColumn
#============= standard library imports ========================

#============= local library imports  ==========================
from script_parser import ScriptParser
class Error(HasTraits):
    '''
    '''
    file = Str
    linenum = Int
    error = Str
class ScriptValidator(HasTraits):
    '''
    '''
    errors = List(Error)
    parser = Instance(ScriptParser)

    def _add_error(self, **kw):
        '''
        '''
        if 'error' in kw:
            if kw['error'] is not None:
                error = Error(**kw)

                self.errors.append(error)

    def validate(self, script, file = None):
        '''
        '''

        #get the parser associated with the script


        text = script.text
        parser = script._script.parser

        #check each line for errors
        #for name, linenum, e in self.parser.parse(text):
        for name, linenum, e in parser.parse(text):
            if isinstance(e, list):
                for name, linei, ei in e:
                    if file is not None:
                        name = file
                    self._add_error(file = name, linenum = linei,
                            error = ei)
            else:
                if file is not None:
                    name = file
                self._add_error(file = name, linenum = linenum, error = e)

    def traits_view(self):
        '''
        '''
        cols = [ObjectColumn(name = 'file'),
              ObjectColumn(name = 'linenum'),
              ObjectColumn(name = 'error')]
        return View(Item('errors', editor = TableEditor(columns = cols,
                                                        editable = False),
                         show_label = False))

    def _parser_default(self):
        '''
        '''
        return ScriptParser()

#============= EOF ====================================