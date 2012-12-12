#===============================================================================
# Copyright 2011 Jake Ross
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



#from numpy import array
#std_holes_positions = array([(1.0, 0.0),
#                                 (0.50000000000000011, 0.8660254037844386),
#                                 (-0.49999999999999978, 0.86602540378443882),
#                                 (-1.0, 1.2246467991473532e-16),
#                                 (-0.50000000000000044, -0.86602540378443837),
#                                 (0.5, -0.8660254037844386)])
#std_js = array([(1., 0.5),
#                (1., 0.5),
#                (1., 0.5),
#                (1., 0.5),
#                (1., 0.5),
#                (1., 0.5)])
#unk_js = array([(1., 0.5),
#                (1., 0.5),
#                (1., 0.5),
#                (1., 0.5),
#                (1., 0.5),
#                (1., 0.5)])
#unknown_holes_positions = array([(0.86602540378443871, 0.49999999999999994),
#                                (6.123233995736766e-17, 1.0),
#                                (-0.86602540378443871, 0.49999999999999994),
#                                (-0.8660254037844386, -0.50000000000000011),
#                                (-1.8369701987210297e-16, -1.0),
#                                (0.86602540378443837, -0.50000000000000044)])
#
#def test():
#    from fmonte_carlo import monte_carlo
#
#    monte_carlo(std_holes_positions,
#                unknown_holes_positions,
#                std_js,
#                unk_js,
#                10000,
#                12
#                )
#
#
#if __name__ == '__main__':
#    from timeit import Timer
#    t = Timer('test()', 'from __main__ import test')
#    print t.timeit(1)
##    t2 = Timer('test()', 'from monte_carlo import test')
##    print t2.timeit(1)
