#============= enthought library imports =======================
from envisage.ui.action.api import Action#, Group, Menu, ToolBar
from envisage.ui.workbench.api import WorkbenchActionSet


#============= standard library imports ========================

#============= local library imports  ==========================

class ExperimentActionSet(WorkbenchActionSet):
    '''
        G{classtree}
    '''
    id = 'pychron.experiment.action_set'
#    menus = [
#           Menu(name = '&File', path = 'MenuBar')
#           ]
    actions = [Action(name = 'New Experiment',
                      path = 'MenuBar/File',
                    class_name = 'src.experiments.plugins.experiment_actions:NewExperimentAction'

                    ),
                Action(name = 'Open Experiment',
                       path = 'MenuBar/File',
                       class_name = 'src.experiments.plugins.experiment_actions:OpenExperimentAction'

                       ),
                Action(name = 'Recall',
                       path = 'MenuBar/File',
                       class_name = 'src.experiments.plugins.experiment_actions:RecallAnalysisAction'

                       )
             ]
#============= EOF ====================================
