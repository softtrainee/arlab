'''
'''
#=============enthought library imports=======================

#=============standard library imports ========================

#=============local library imports  ==========================

class Panner:
    def click(self, pt):
        '''
        '''
        self.start_pt = pt
    def drag(self, pt):
        '''
        '''
        scale = 16.5
        t = [(self.start_pt[0] - pt[0]) / scale, (self.start_pt[1] - pt[1]) / scale, 0]
        self.click(pt)
        return t
