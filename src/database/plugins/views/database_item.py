#'''
#Copyright 2011 Jake Ross
#
#Licensed under the Apache License, Version 2.0 (the "License");
#you may not use this file except in compliance with the License.
#You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
#Unless required by applicable law or agreed to in writing, software
#distributed under the License is distributed on an "AS IS" BASIS,
#WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#See the License for the specific language governing permissions and
#limitations under the License.
#'''
##============= enthought library imports =======================
#from traits.api import HasTraits
#
##============= standard library imports ========================
#
##============= local library imports  ==========================
#class DatabaseItem(HasTraits):
#    def get_items(self, id):
#        '''
#        '''
#        print getattr(self, '_{}'.format(id))
#        return [i[1] for i in getattr(self, '_{}'.format(id))]
#
#    def get_id(self, id):
#        '''
#        '''
#        attr = getattr(self, id)
#        for i in getattr(self, '_{}'.format(id)):
#            if i[1] == attr:
#                return int(i[0])
##============= views ===================================
##============= EOF ====================================
