#  Copyright (c) 2021 John Carrino
import struct
from typing import Dict, Union
from dataclasses import dataclass

import numpy as np
import math

from frispy.environment import Environment
from frispy.model import Model
from frispy.trajectory import Trajectory
from scipy.spatial.transform import Rotation


@dataclass
class ThrowData:
    NUM_POINTS = 2000
    SENSORS_GRAVITY_STANDARD = 9.80665
    SENSORS_DPS_TO_RADS = 0.017453293
    OUTPUT_SCALE_FACTOR_400G = (SENSORS_GRAVITY_STANDARD * 400 / ((1 << 15) - 1))
    OUTPUT_SCALE_FACTOR_32G = (SENSORS_GRAVITY_STANDARD * 32 / ((1 << 15) - 1))
    OUTPUT_SCALE_FACTOR_4000DPS = (SENSORS_DPS_TO_RADS * 4000 / ((1 << 15) - 1))

    version: int
    durationMicros: list[int]
    accel0: list[np.ndarray]
    gyros: list[np.ndarray]
    accel1: list[np.ndarray]
    accel2: list[np.ndarray]
    endQ: Rotation
    temperature: float
    type: int

    def getStartingRotation(self) -> Rotation:
        q: Rotation = self.endQ
        for i in reversed(range(ThrowData.NUM_POINTS)):
            duration: float = self.durationMicros[i] / 1_000_000.0
            delta = self.gyros[i] * duration
            rot: Rotation = Rotation.from_euler('XYZ', [delta[0], delta[1], delta[2]])
            q = q * rot.inv()
        return q


    @staticmethod
    def readUnsignedShort(f) -> int:
        buf = f.read(2)
        return struct.unpack('<H', buf)[0]

    @staticmethod
    def readShort(f) -> int:
        buf = f.read(2)
        return struct.unpack('<h', buf)[0]

    @staticmethod
    def readFloat(f) -> float:
        buf = f.read(4)
        return struct.unpack('<f', buf)[0]

    @staticmethod
    def readVector(f, scaleFactor: float) -> np.ndarray:
        x = ThrowData.readShort(f) * scaleFactor
        y = ThrowData.readShort(f) * scaleFactor
        z = ThrowData.readShort(f) * scaleFactor
        return np.array([x, y, z])

    @staticmethod
    def readFile(fileName: str):
        with open(fileName, "rb") as f:
            return ThrowData.readFromFile(f)

    @staticmethod
    def readFromFile(f):
        numPoints = ThrowData.NUM_POINTS
        version = ThrowData.readUnsignedShort(f)
        startIndex = ThrowData.readUnsignedShort(f)
        lastIndex = ThrowData.readUnsignedShort(f)
        type = ThrowData.readUnsignedShort(f)
        durationMicros = [None] * numPoints
        for i in range(numPoints):
            durationMicros[(i - startIndex + numPoints) % numPoints] = ThrowData.readUnsignedShort(f)

        accel0 = [None] * numPoints
        gyros = [None] * numPoints
        accel1 = [None] * numPoints
        accel2 = [None] * numPoints
        for i in range(numPoints):
            accel0[(i - startIndex + numPoints) % numPoints] = ThrowData.readVector(f, ThrowData.OUTPUT_SCALE_FACTOR_32G)

        for i in range(numPoints):
            gyros[(i - startIndex + numPoints) % numPoints] = ThrowData.readVector(f, ThrowData.OUTPUT_SCALE_FACTOR_4000DPS)

        for i in range(numPoints):
            accel1[(i - startIndex + numPoints) % numPoints] = ThrowData.readVector(f, ThrowData.OUTPUT_SCALE_FACTOR_400G)

        for i in range(numPoints):
            accel2[(i - startIndex + numPoints) % numPoints] = ThrowData.readVector(f, ThrowData.OUTPUT_SCALE_FACTOR_400G)

        qw = ThrowData.readFloat(f)
        qx = ThrowData.readFloat(f)
        qy = ThrowData.readFloat(f)
        qz = ThrowData.readFloat(f)
        rotation: Rotation = Rotation.from_quat([qx, qy, qz, qw])
        temp = ThrowData.readFloat(f)
        return ThrowData(version, durationMicros, accel0, gyros, accel1, accel2, rotation, temp, type)
