'''
Copyright 2011 Jake Ross

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''
#=============enthought library imports=======================
from traits.api import HasTraits, List, Any
from traitsui.api import View, Item
#============= standard library imports ========================
#============= local library imports  ==========================
from src.managers.manager import Manager
from datetime import datetime
class Run(object):
    rid = None
    start = None
    end = None
    def __init__(self, rid):
        self.rid = rid
        self.start = datetime.strftime(datetime.today(), '%Y-%m-%d %H:%M:%S')
        
    def set_complete_time(self):
        self.end = datetime.strftime(datetime.today(), '%Y-%m-%d %H:%M:%S')
        
    def to_report(self):
        return '{:<15}{:<30}{}'.format(self.rid, self.start, self.end)
    
class Report(HasTraits):
    name = None
    runs = List(Run)
    start = None
    end = None
    def __init__(self, name, *args, **kw):
        super(Report, self).__init__(*args, **kw)
        self.name = name
        self.start = datetime.strftime(datetime.today(), '%Y-%m-%d %H:%M:%S')
        
    def complete(self):
        self.end = datetime.strftime(datetime.today(), '%Y-%m-%d %H:%M:%S')
        
    def complete_run(self):
        self.runs[-1].set_complete_time()
        
    def start_run(self, r):
        self.runs.append(Run(r))
        
    def generate_report(self):
        multruns_info = '{}\nStart: {}\nEnd  :{}'.format(self.name,
                                                         self.start,
                                                         self.end)
        header = '{:<15}{:<30}{}'.format('Name', 'Start', 'End')
        runs = '\n'.join([r.to_report() for r in self.runs])
    
        return '\n'.join([multruns_info, header, runs])
        
        
class MultrunsReportManager(Manager):
    email_manager = Any
    current_report = None
    def start_new_report(self, name):
        self.current_report = Report(name)
        
    def complete_report(self):
        if self.current_report is not None:
            self.current_report.complete()
            self.send_report()
            
        
    def start_run(self, r):
        if self.current_report is not None:
            print 'start run'
            self.current_report.start_run(r)
        
    def complete_run(self):
        if self.current_report is not None:
            self.current_report.complete_run()
        

    def send_report(self):
        if self.application is not None:        
            em = self.application.get_service('src.social.email_manager.EmailManager')
            if em is not None:
                if self.current_report is not None:
                    text = self.current_report.generate_report()
                    em.broadcast(text, subject='MultRuns Report')
        
#============= EOF =====================================
