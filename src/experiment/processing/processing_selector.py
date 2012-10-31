#===============================================================================
# Copyright 2012 Jake Ross
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#   http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#===============================================================================

#============= enthought library imports =======================
from traits.api import HasTraits, List, Instance, DelegatesTo, Button, Property, Str, Int, \
    Event, Any
from traitsui.api import View, Item, HGroup, VGroup, spring, HSplit, \
    InstanceEditor, ListStrEditor, EnumEditor, Spring
from src.database.core.database_adapter import DatabaseAdapter
from traitsui.list_str_adapter import ListStrAdapter
from traitsui.editors.tabular_editor import TabularEditor as traitsTabularEditor, \
    TabularEditor
from traitsui.tabular_adapter import TabularAdapter
from src.viewable import Viewable
from src.database.core.database_selector import ColumnSorterMixin
from src.helpers.color_generators import colorname_generator

#============= standard library imports ========================
#============= local library imports  ==========================
#from traitsui.wx.tabular_editor import TabularEditor as wxTabularEditor
#from traitsui.basic_editor_factory import BasicEditorFactory
#
#class _TabularEditor(wxTabularEditor):
#    def init(self, parent):
#        super(_TabularEditor, self).init(parent)
#        print parent
#        print parent.GetSizeTuple()
#        
#class TabularEditor(traitsTabularEditor):
#
#    def _get_klass(self):
#        return _TabularEditor

#class LAdapter(ListStrAdapter):
#
##    def get_bg_color(self, obj, trait, row):
#    def get_text_color(self, obj, trait, row):
##        print obj, trait, row
#        o = getattr(obj, trait)[row]
#
#        if 'group_marker' in str(o):
#            return 'red'
#        else:
#            return 'black'
#
#    def get_text(self, obj, tr, ind):
#
#        o = getattr(obj, tr)[ind]
#        if 'group_marker' in str(o):
#            return '-----------------------'
#        elif 'mean_marker' in str(o):
#            return '***********************'
#        else:
#            return o


class SelectedrecordsAdapter(TabularAdapter):
    labnumber_width = Int(90)
    rid_width = Int(50)

    aliquot_text = Property
#    rid_text = Property
    text_color = Property
    font = 'monospace'

    def _get_text_color(self):
        return self.item.color

#    def _get_rid_text(self):
#        if self.item.rid == ' ':
#            return ' '
#            return '---'
#        elif self.item.rid == '***':
#            return '***'
#        else:
#            return '{:05n}'.format(self.item.rid)

    def _columns_default(self):
        cols = [
                #('ID', 'rid'),
                ('Labnumber', 'labnumber'),
                ('Aliquot', 'aliquot'),
                ('Group', 'group_id'),
                ('Graph', 'graph_id')
                ]
        return cols

    def _get_aliquot_text(self, trait, item):
        return '{}{}'.format(self.item.aliquot, self.item.step)

class Marker(HasTraits):
    color = 'white'
    def __getattr__(self, attr):
        return ' '


class ProcessingSelector(Viewable, ColumnSorterMixin):
    selected_record_labels = Property(depends_on='selected_records')
    selected_records = List
    db = Instance(DatabaseAdapter)

    selector = DelegatesTo('db')

    append = Button
    replace = Button
    project = Str('---')
    projects = Property
    machine = Str('---')
    machines = Property
    analysis_type = Str('---')
    analysis_types = Property

    add_group_marker = Button('Set Group')
    graph_by_labnumber = Button('Graph By Labnumber')
#    add_mean_marker = Button('Set Mean')

    update_data = Event

    selected_row = Any
    selected = Any
    group_cnt = 0

    def _load_selected_records(self):
        for r in self.selector.selected:
            if r not in self.selected_records:
                self.selected_records.append(r)

        self.selected_row = self.selected_records[-1]

    def close(self, isok):
        if isok:
            self.update_data = True
        return True

#===============================================================================
# handlers
#===============================================================================
    def _graph_by_labnumber_fired(self):
        groups = dict()
        for ri in self.selected_records:
            if ri.labnumber in groups:
                group = groups[ri.labnumber]
                group.append(ri.labnumber)
            else:
                groups[ri.labnumber] = [ri.labnumber]

        keys = sorted(groups.keys())
        for ri in self.selected_records:
            ri.graph_id = keys.index(ri.labnumber)


    def _add_group_marker_fired(self):
        for r in self.selected:
            self.group_cnt += 1
            r.group_id = self.group_cnt
            r.color = 'red'

        oruns = set(self.selected_records) ^ set(self.selected)
        self.selected_records = list(oruns) + [Marker()] + self.selected

#    def _add_mean_marker_fired(self):
#        pass

    def _append_fired(self):
        self._load_selected_records()

    def _replace_fired(self):
        self.selected_records = []
        self._load_selected_records()

    def _project_changed(self):
        #get all analyses of this project
        db = self.db
        selector = self.selector

        pr = self.project
        if pr == '---':
            return

        if pr == 'recent':
            if self.machine == '---':
                selector.load_recent()
                return

            nrs = selector.get_recent()
            nrs = [ni for ni in nrs if ni.measurement.mass_spectrometer.name == self.machine]

        else:
            def exclude(ai):
                a = False
                b = False
                if self.machine != '---':
                    a = ai.measurement.mass_spectrometer.name != self.machine
                if self.analysis_type != '---':
                    b = ai.measurement.analysis_type.name != self.analysis_type
                return a or b

            pi = db.get_project(pr)
            nrs = [an for s in pi.samples
                    for ln in s.labnumbers
                        for an in ln.analyses if not exclude(an)]

        selector.load_records(nrs)

    def _machine_changed(self):
        db = self.db
        selector = self.selector

        ma = self.machine
        if ma == '---':
            return

        mi = db.get_mass_spectrometer(ma)

        at = self.analysis_type.lower()
        def exclude(meas):
            if at != '---':
                try:
                    return meas.analysis_type.name != at
                except AttributeError:
                    return True

        nrs = [me.analysis for me in mi.measurements if not exclude(me)]
        selector.load_records(nrs)

    def _analysis_type_changed(self):
        db = self.db
        selector = self.selector

        at = self.analysis_type.lower()
        if at == '---':
            return

        atype = db.get_analysis_type(at)
        pr = self.project
        ma = self.machine
        def exclude(meas):
            m = False
            p = False
            if ma != '---':
                try:
                    m = meas.mass_spectrometer.name != ma
                except AttributeError, e:
                    print e

            if pr != '---':
                p = meas.analysis.labnumber.sample.project != pr
            return m or p

        nrs = [mi.analysis for mi in atype.measurements if not exclude(mi)]

        selector.load_records(nrs)

#===============================================================================
# view
#===============================================================================
    def traits_view(self):

        cntrl_grp = VGroup(
                           Item('project', editor=EnumEditor(name='projects'),
                                show_label=False,
#                                width= -80
                                ),
                           Item('machine', editor=EnumEditor(name='machines'),
                                show_label=False,
#                                width= -80
                                ),
                           Item('analysis_type', editor=EnumEditor(name='analysis_types'),
                                show_label=False,
#                                width= -80
                                ),

                           )
        selector_grp = VGroup(
                              HGroup(
                                     Item('append', show_label=False, width= -80),
                                     Item('replace', show_label=False, width= -80),
#                                     Spring(springy=False, width= -50),
                                     Item('object.selector.limit')
                                     ),
                              Item('selector',
                                   show_label=False, style='custom',
                                   editor=InstanceEditor(view='panel_view'),
                                   width=300
#                                   width=0.75,
                                )
                              )


        selected_grp = VGroup(
                              Item('selected_records',
                                          show_label=False,
                                          style='custom',
                                          editor=TabularEditor(
                                                               multi_select=True,
                                                               auto_update=True,
                                                        editable=False,
#                                                        drag_move=True,
                                                        selected='object.selected',
                                                        selected_row='object.selected_row',
                                                        column_clicked='object.column_clicked',
#                                                        operations=['drag']
                                                        adapter=SelectedrecordsAdapter(
#                                                                                       can_drop=True,
#                                                                                       can_edit=True
                                                                                       ),
                                                        ),
#                                          width=0.25,
                                          width= -140
                                          ),
#                                    springy=False
                                Item('add_group_marker', show_label=False),
                                Item('graph_by_labnumber', show_label=False),
#                                Item('add_mean_marker', show_label=False)
                                )


        v = View(HGroup(
                        spring,
                        cntrl_grp,
                        HSplit(selector_grp,
                               selected_grp)

#                        selection_grp,

                      ),
                  handler=self.handler_klass,
                  buttons=['OK', 'Cancel'],
#                  width=900,
                  height=500,
                  resizable=True,
                  id='processing_selector',
                  title='Manage Data'

               )

        return v

#===============================================================================
# property get/set
#===============================================================================
    def _get_projects(self):
        db = self.db
#        db.reset()
        prs = ['---', 'recent']
        ps = db.get_projects()
        if ps:
            prs += [p.name for p in ps]
        return prs

    def _get_machines(self):
        db = self.db
#        db.reset()
        mas = ['---']
        ms = db.get_mass_spectrometers()
        if ms:
            mas += [m.name for m in ms]
        return mas

    def _get_analysis_types(self):
        db = self.db
        ats = ['---']
        ai = db.get_analysis_types()
        if ai:
            ats += [aii.name.capitalize() for aii in ai]

        return ats
#        return ['Blank', 'Air', 'Unknown']

    def _get_selected_record_labels(self):
        return ['{} {}'.format(r.rid, r.labnumber) for r in self.selected_records]


#============= EOF =============================================
