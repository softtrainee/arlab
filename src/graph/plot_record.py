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
class PlotRecord(object):
    data = None
    plotids = None
    def __init__(self, data, plotids, labels, *args, **kw):
        self.data = data
        self.plotids = plotids
        self.labels = labels
        
    def as_data_tuple(self):
        try:
            return tuple(self.data)
        except TypeError:
            return (self.data,)
        
    def __str__(self, *args, **kwargs):
        fmt_str = '{}={:0.3f}'
        s = []
        for a in zip(self.labels, self.data):
            s.append(fmt_str.format(*a))
        
        return ', '.join(s)
