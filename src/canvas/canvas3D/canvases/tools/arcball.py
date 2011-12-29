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

"""
ArcBall.py -- Math utilities, vector, matrix types and ArcBall quaternion rotation class

>>> unit_test_ArcBall_module ()
unit testing ArcBall
Quat for first drag
[ 0.08438914 -0.08534209 -0.06240178  0.99080837]
First transform
[[ 0.97764552 -0.1380603   0.15858325  0.        ]
 [ 0.10925253  0.97796899  0.17787792  0.        ]
 [-0.17964739 -0.15657592  0.97119039  0.        ]
 [ 0.          0.          0.          1.        ]]
LastRot at end of first drag
[[ 0.97764552 -0.1380603   0.15858325]
 [ 0.10925253  0.97796899  0.17787792]
 [-0.17964739 -0.15657592  0.97119039]]
Quat for second drag
[ 0.00710336  0.31832787  0.02679029  0.94757545]
Second transform
[[ 0.88022292 -0.08322023 -0.46720669  0.        ]
 [ 0.14910145  0.98314685  0.10578787  0.        ]
 [ 0.45052907 -0.16277808  0.8777966   0.        ]
 [ 0.          0.          0.          1.00000001]]
"""

from numpy import dot, zeros, identity, sum
import copy
from math import sqrt

# //assuming IEEE-754(GLfloat), which i believe has max precision of 7 bits
Epsilon = 1.0e-5


class ArcBallT:
    def __init__ (self, NewWidth, NewHeight):
        '''
            @type NewWidth: C{str}
            @param NewWidth:

            @type NewHeight: C{str}
            @param NewHeight:
        '''
        self.m_StVec = Vector3fT ()
        self.m_EnVec = Vector3fT ()
        self.m_AdjustWidth = 1.0
        self.m_AdjustHeight = 1.0
        self.setBounds (NewWidth, NewHeight)

    def __str__ (self):
        '''
        '''
        str_rep = ""
        str_rep += "StVec = " + str (self.m_StVec)
        str_rep += "\nEnVec = " + str (self.m_EnVec)
        str_rep += "\n scale coords %f %f" % (self.m_AdjustWidth, self.m_AdjustHeight)
        return str_rep

    def setBounds (self, NewWidth, NewHeight):
        '''
            @type NewWidth: C{str}
            @param NewWidth:

            @type NewHeight: C{str}
            @param NewHeight:
        '''
        # //Set new bounds
        assert (NewWidth > 1.0 and NewHeight > 1.0), "Invalid width or height for bounds."
        # //Set adjustment factor for width/height
        self.m_AdjustWidth = 1.0 / ((NewWidth - 1.0) * 0.5)
        self.m_AdjustHeight = 1.0 / ((NewHeight - 1.0) * 0.5)

    def _mapToSphere (self, NewPt):
        '''
            @type NewPt: C{str}
            @param NewPt:
        '''
        # Given a new window coordinate, will modify NewVec in place
        X = 0
        Y = 1
        Z = 2

        NewVec = Vector3fT ()
        # //Copy paramter into temp point
        TempPt = copy.copy (NewPt)
        # //Adjust point coords and scale down to range of [-1 ... 1]
        TempPt [X] = (NewPt [X] * self.m_AdjustWidth) - 1.0
        TempPt [Y] = 1.0 - (NewPt [Y] * self.m_AdjustHeight)
        # //Compute the square of the length of the vector to the point from the center
        length = sum (dot (TempPt, TempPt))
        # //If the point is mapped outside of the sphere... (length > radius squared)
        radius = 1.0
        if (length > radius):
            # //Compute a normalizing factor (radius / sqrt(length))
            norm = radius / sqrt (length);

            # //Return the "normalized" vector, a point on the sphere
            NewVec [X] = TempPt [X] * norm;
            NewVec [Y] = TempPt [Y] * norm;
            NewVec [Z] = 0.0;
        else:            # //Else it's on the inside
            # //Return a vector to a point mapped inside the sphere sqrt(radius squared - length)
            NewVec [X] = TempPt [X]
            NewVec [Y] = TempPt [Y]
            NewVec [Z] = sqrt (radius - length)

        return NewVec

    def click (self, NewPt):
        '''
            @type NewPt: C{str}
            @param NewPt:
        '''
        # //Mouse down (Point2fT
        self.m_StVec = self._mapToSphere (NewPt)
        return

    def drag (self, NewPt):
        '''
            @type NewPt: C{str}
            @param NewPt:
        '''
        # //Mouse drag, calculate rotation (Point2fT Quat4fT)
        """ drag (Point2fT mouse_coord) -> new_quaternion_rotation_vec
        """
        X = 0
        Y = 1
        Z = 2
        W = 3

        self.m_EnVec = self._mapToSphere (NewPt)

        # //Compute the vector perpendicular to the begin and end vectors
        # Perp = Vector3fT ()
        Perp = Vector3fCross(self.m_StVec, self.m_EnVec);

        NewRot = Quat4fT ()
        # //Compute the length of the perpendicular vector
        if (Vector3fLength(Perp) > Epsilon):        #    //if its non-zero
            # //We're ok, so return the perpendicular vector as the transform after all
            NewRot[X] = Perp[X];
            NewRot[Y] = Perp[Y];
            NewRot[Z] = Perp[Z];
            # //In the quaternion values, w is cosine (theta / 2), where theta is rotation angle
            NewRot[W] = Vector3fDot(self.m_StVec, self.m_EnVec);
        else:        #                            //if its zero
            # //The begin and end vectors coincide, so return a quaternion of zero matrix (no rotation)
            NewRot[X] = NewRot[Y] = NewRot[Z] = NewRot[W] = 0.0;

        return NewRot


# ##################### Math utility ##########################################


def Matrix4fT ():
    '''
    '''
    return identity (4, 'f')

def Matrix3fT ():
    '''
    '''
    return identity (3, 'f')

def Quat4fT ():
    '''
    '''
    return zeros (4, 'f')

def Vector3fT ():
    '''
    '''
    return zeros (3, 'f')

def Point2fT (x=0.0, y=0.0):
    '''
        @type y: C{str}
        @param y:
    '''
    pt = zeros (2, 'f')
    pt [0] = x
    pt [1] = y
    return pt

def Vector3fDot(u, v):
    '''
        @type v: C{str}
        
        @param v:
    '''
    # Dot product of two 3f vectors
    dotprod = dot (u, v)
    return dotprod

def Vector3fCross(u, v):
    '''
        @type v: C{str}
        @param v:
    '''
    # Cross product of two 3f vectors
    X = 0
    Y = 1
    Z = 2
    cross = zeros (3, 'f')
    cross [X] = (u[Y] * v[Z]) - (u[Z] * v[Y])
    cross [Y] = (u[Z] * v[X]) - (u[X] * v[Z])
    cross [Z] = (u[X] * v[Y]) - (u[Y] * v[X])
    return cross

def Vector3fLength (u):
    '''
    '''
    mag_squared = sum(dot (u, u))
    mag = sqrt (mag_squared)
    return mag

def Matrix3fSetIdentity ():
    '''
    '''
    return identity (3, 'f')

def Matrix3fMulMatrix3f (matrix_a, matrix_b):
    '''
        @type matrix_b: C{str}
        @param matrix_b:
    '''
    return dot (matrix_a, matrix_b)




def Matrix4fSVD (NewObj):
    '''
    '''
    X = 0
    Y = 1
    Z = 2
    s = sqrt (
        ((NewObj [X][X] * NewObj [X][X]) + (NewObj [X][Y] * NewObj [X][Y]) + (NewObj [X][Z] * NewObj [X][Z]) +
        (NewObj [Y][X] * NewObj [Y][X]) + (NewObj [Y][Y] * NewObj [Y][Y]) + (NewObj [Y][Z] * NewObj [Y][Z]) +
        (NewObj [Z][X] * NewObj [Z][X]) + (NewObj [Z][Y] * NewObj [Z][Y]) + (NewObj [Z][Z] * NewObj [Z][Z])) / 3.0)
    return s

def Matrix4fSetRotationScaleFromMatrix3f(NewObj, three_by_three_matrix):
    '''
        @type three_by_three_matrix: C{str}
        @param three_by_three_matrix:
    '''
    # Modifies NewObj in-place by replacing its upper 3x3 portion from the 
    # passed in 3x3 matrix.
    # NewObj = Matrix4fT ()
    NewObj [0:3, 0:3] = three_by_three_matrix
    return NewObj

# /**
# * Sets the rotational component (upper 3x3) of this matrix to the matrix
# * values in the T precision Matrix3d argument; the other elements of
# * this matrix are unchanged; a singular value decomposition is performed
# * on this object's upper 3x3 matrix to factor out the scale, then this
# * object's upper 3x3 matrix components are replaced by the passed rotation
# * components, and then the scale is reapplied to the rotational
# * components.
# * @param three_by_three_matrix T precision 3x3 matrix
# */
def Matrix4fSetRotationFromMatrix3f (NewObj, three_by_three_matrix):
    '''
        @type three_by_three_matrix: C{str}
        @param three_by_three_matrix:
    '''
    scale = Matrix4fSVD (NewObj)

    NewObj = Matrix4fSetRotationScaleFromMatrix3f(NewObj, three_by_three_matrix);
    scaled_NewObj = NewObj * scale             # Matrix4fMulRotationScale(NewObj, scale);
    return scaled_NewObj

def Matrix3fSetRotationFromQuat4f (q1):
    '''
    '''
    # Converts the H quaternion q1 into a new equivalent 3x3 rotation matrix. 
    X = 0
    Y = 1
    Z = 2
    W = 3

    NewObj = Matrix3fT ()
    n = sum (dot (q1, q1))
    s = 0.0
    if (n > 0.0):
        s = 2.0 / n
    xs = q1 [X] * s;  ys = q1 [Y] * s;  zs = q1 [Z] * s
    wx = q1 [W] * xs; wy = q1 [W] * ys; wz = q1 [W] * zs
    xx = q1 [X] * xs; xy = q1 [X] * ys; xz = q1 [X] * zs
    yy = q1 [Y] * ys; yz = q1 [Y] * zs; zz = q1 [Z] * zs
    # This math all comes about by way of algebra, complex math, and trig identities.
    # See Lengyel pages 88-92
    NewObj [X][X] = 1.0 - (yy + zz);    NewObj [Y][X] = xy - wz;             NewObj [Z][X] = xz + wy;
    NewObj [X][Y] = xy + wz;         NewObj [Y][Y] = 1.0 - (xx + zz);    NewObj [Z][Y] = yz - wx;
    NewObj [X][Z] = xz - wy;         NewObj [Y][Z] = yz + wx;              NewObj [Z][Z] = 1.0 - (xx + yy)

    return NewObj




