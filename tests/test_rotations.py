#  Copyright (c) 2021 John Carrino
import math
from pprint import pprint
from unittest import TestCase
import numpy as np
import numpy.testing as npt
from scipy.spatial.transform import Rotation


class TestRotations(TestCase):
    def test_euler_to_quat(self):
        downhill = -15 * math.pi / 180
        anhyzer = -5 * math.pi / 180
        nose_down = -2 * math.pi / 180
        yTot = downhill + nose_down
        #rotation = Rotation.from_euler("xy", [anhyzer, nose_down])
        rotation = Rotation.from_euler("YXY", [downhill, anhyzer, nose_down])

        #discBot = Quaternions.rotate(rotation, GyroDataReader.PLUS_Z);
        R = rotation.as_matrix()
        # Unit vectors
        plusZ = np.array([0, 0, 1])
        discBot = R @ plusZ
        endDirection = np.array([math.cos(downhill), 0, -math.sin(downhill)])
        dot = discBot @ endDirection
        computedNoseAngle = math.pi/2 - math.acos(dot)
        discBot -= dot * endDirection
        discBot /= np.linalg.norm(discBot)

        fullHyzer = np.cross(plusZ, endDirection)
        fullHyzer /= np.linalg.norm(fullHyzer)
        dotHyzer = -discBot @ fullHyzer
        computedAnhyzer = math.pi/2 - math.acos(dotHyzer)
        np.testing.assert_almost_equal(nose_down, computedNoseAngle)
        np.testing.assert_almost_equal(anhyzer, computedAnhyzer)



