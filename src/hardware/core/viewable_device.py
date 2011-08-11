#=============enthought library imports=======================
from traits.api import Instance, Str, Property, Bool, CStr
from traitsui.api import View, Item, Group, VGroup
#=============standard library imports ========================
#=============local library imports  ==========================
from src.config_loadable import ConfigLoadable
from src.graph.graph import Graph
class ViewableDevice(ConfigLoadable):
    '''
        G{classtree}
    '''

    graph = Instance(Graph)
    simulation = Property

    connected = Property(depends_on = 'simulation')
    com_class = Property

    loaded = Property(depends_on = '_loaded')
    _loaded = Bool

    klass = Property
    config_short_path = Property

    last_command = Str
    last_response = Str

    last_value = CStr

    def _get_config_short_path(self):
        '''
            config_path is an attribute of 
        '''
        items = self.config_path.split('/')
        return '/'.join(items[6:])

    def _get_loaded(self):
        return 'Yes' if self._loaded else 'No'

    def _get_klass(self):
        return self.__class__.__name__

    def _get_com_class(self):
        return self._communicator.__class__.__name__

    def _get_connected(self):
        return 'Yes' if not self._get_simulation() else 'No'

    def _get_simulation(self):
        '''
        '''
        if self._communicator is not None:
            return self._communicator.simulation
        else:
            return True

    def current_state_view(self):
        v = View(Item('name'),
                 Item('last_command', style = 'readonly'),
                 Item('last_response', style = 'readonly'),
                 Item('last_value', style = 'readonly')
                 )

        return v
    def _graph_default(self):
        g = Graph(
                  container_dict = dict(padding = [10, 10, 10, 10])
                  )

        self.graph_builder(g)

        return g
    def graph_builder(self, g):
        g.new_plot(padding = [40, 5, 5, 20],
                   zoom = True,
                  pan = True,
                   )
    def get_control_group(self):
        pass

    def info_view(self):
        v = View(
                 Group(
                       VGroup(
                         Item('name', style = 'readonly'),
                         Item('klass', style = 'readonly', label = 'Class'),
                         Item('connected', style = 'readonly'),
                         Item('com_class', style = 'readonly', label = 'Com. Class'),
                         Item('config_short_path', style = 'readonly'),
                         Item('loaded', style = 'readonly'),
                         label = 'Info',
                         ),
                       layout = 'tabbed'
                       )
                 )
        cg = self.get_control_group()

        if cg:
            cg.label = 'Control'
            v.content.content.insert(0, cg)
        return v

    def traits_view(self):


        v = View()
        cg = self.get_control_group()
        if cg:
            v.content.content.append(cg)
        return v
