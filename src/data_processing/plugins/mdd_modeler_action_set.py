#============= enthought library imports =======================
from envisage.ui.action.api import Action#, Group, Menu, ToolBar
from envisage.ui.workbench.api import WorkbenchActionSet


#============= standard library imports ========================

#============= local library imports  ==========================

class MDDModelerActionSet(WorkbenchActionSet):
    '''
        G{classtree}
    '''
    id = 'pychron.mdd.action_set'
#    menus = [
#           Menu(name = '&File', path = 'MenuBar')
#           ]
    actions = [
               Action(name = 'Run Model',
                      path = 'MenuBar/MDD',
                    class_name = 'src.data_processing.plugins.mdd_modeler_actions:RunModelAction'
                    ),
               Action(name = 'Run Configuration',
                      path = 'MenuBar/MDD',
                    class_name = 'src.data_processing.plugins.mdd_modeler_actions:RunConfigurationAction'
                    ),
               Action(name = 'Parse Autoupdate',
                      path = 'MenuBar/MDD',
                    class_name = 'src.data_processing.plugins.mdd_modeler_actions:ParseAutoupdateAction'
                    ),
               Action(name = 'New Model',
                      path = 'MenuBar/MDD',
                    class_name = 'src.data_processing.plugins.mdd_modeler_actions:NewModelAction'
                    ),
             ]
#============= EOF ====================================
