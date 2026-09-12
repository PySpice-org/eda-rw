####################################################################################################
#
# EDA-RW — Python library to read/write EDA Sexpr file format
# Copyright (C) 2021 Fabrice SALVAIRE
# SPDX-License-Identifier: AGPL-3.0-or-later
#
####################################################################################################

"""This module provides a basic implementation for geometry primitive like Position, Vector and
EuclidianMatrix.

"""

####################################################################################################

__all__ = [
    'EuclidianMatrix',
    'Position',
    'PositionAngle',
    'Vector',
]

####################################################################################################

import math
from collections.abc import Iterator

####################################################################################################

EPSILON = 1e-4  # numerical tolerance to match coordinate

####################################################################################################

type Matrix2D = tuple[tuple[int, int], tuple[int, int]]

class EuclidianMatrix:

    ##############################################

    @classmethod
    def identity(cls) -> EuclidianMatrix:
        _ = ((1, 0),
             (0, 1))
        return cls(_)

    ##############################################

    @classmethod
    def parity(cls) -> EuclidianMatrix:
        _ = ((-1, +0),
             (+0, -1))
        return cls(_)

    ##############################################

    @classmethod
    def rotation(cls, angle: int) -> EuclidianMatrix:
        match angle:
            case 0:
                return cls.identity()
            case 90 | -270:
                _ = ((0, -1),
                     (1, +0))
            case 180 | -180:
                # mirror x and y
                _ = ((-1, 0),
                     (+0, -1))
            case 270 | -90:
                # 90 and mirror y
                _ = ((+0, 1),
                     (-1, 0))
            case _:
                raise NotImplementedError(f"angle {angle}")
        return cls(_)

    ##############################################

    def __init__(self, matrix: Matrix2D) -> None:
        self.m = matrix

    ##############################################

    @property
    def flat(self) -> tuple[int, int, int, int]:
        return tuple(list(self.m[0]) + list(self.m[1]))  # ty: ignore[invalid-return-type]

    # def __getitem__(self, ) -> int:

    ##############################################

    def __mul__(self, matrix: EuclidianMatrix) -> EuclidianMatrix:
        a00, a01, a10, a11 = self.flat
        b00, b01, b10, b11 = matrix.flat
        # m_ij = a_ik * b_kj
        m00 = a00 * b00 + a01 * b10
        m10 = a10 * b00 + a11 * b10
        m01 = a00 * b01 + a01 * b11
        m11 = a10 * b01 + a11 * b11
        _ = ((m00, m01), (m10, m11))
        return self.__class__(_)

    ##############################################

    @property
    def x_mirror(self) -> EuclidianMatrix:
        m00, m01, m10, m11 = self.flat
        _ = ((-m00, -m01),
             (+m10, +m11))
        return self.__class__(_)

    @property
    def y_mirror(self) -> EuclidianMatrix:
        m00, m01, m10, m11 = self.flat
        _ = ((+m00, +m01),
             (-m10, -m11))
        return self.__class__(_)

    @property
    def xy_mirror(self) -> EuclidianMatrix:
        # self * parity
        m00, m01, m10, m11 = self.flat
        _ = ((-m00, +m01),
             (+m10, -m11))
        return self.__class__(_)

####################################################################################################

class Position:

    ##############################################

    def __init__(self, x: float = 0, y: float = 0) -> None:
        self._x = x
        self._y = y

    ##############################################

    @property
    def x(self) -> float:
        return self._x

    @property
    def y(self) -> float:
        return self._y

    @property
    def xy(self) -> tuple[float, float]:
        return self._x, self._y

    def __len__(self) -> int:
        return 2

    def __iter__(self) -> Iterator[float]:
        return iter(self.xy)

    def __getitem__(self, index: int) -> float:
        return self.xy[index]

    ##############################################

    def __repr__(self) -> str:
        return f"Pxy=({self._x:.2f}, {self._y:.2f})"

    ##############################################

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Position):
            return False
        return (math.fabs(self._x - other.x) < EPSILON and
                math.fabs(self._y - other.y) < EPSILON)

    ##############################################

    def __add__(self, position: Position) -> Vector:
        return Vector(self._x + position.x, self._y + position.y)

    ##############################################

    def __sub__(self, position: Position) -> Vector:
        return Vector(self._x - position.x, self._y - position.y)

    ##############################################

    def __mul__(self, matrix: EuclidianMatrix) -> Vector:
        m00, m01, m10, m11 = matrix.flat
        x = m00 * self._x + m01 * self._y
        y = m10 * self._x + m11 * self._y
        return Vector(x, y)

####################################################################################################

class Vector(Position):

    @classmethod
    def direction(self, length: float, angle: int) -> Vector:
        return Vector(length) * EuclidianMatrix.rotation(angle)

    ##############################################

    def __str__(self) -> str:
        return f"Vxy=({self._x:.2f}, {self._y:.2f})"

    ##############################################

    @property
    def is_vertical(self) -> bool:
        return math.fabs(self._x) < EPSILON

    @property
    def is_horizontal(self) -> bool:
        return math.fabs(self._y) < EPSILON

    ##############################################

    def scalar_product(self, vector: Vector) -> float:
        return self._x * vector.x + self._y * vector.y

    ##############################################

    def vectorial_product(self, vector: Vector) -> float:
        return self._x * vector.y - self._y * vector.x

    ##############################################

    def length(self) -> float:
        return math.sqrt(self.scalar_product(self))

    ##############################################

    @classmethod
    def point_in_segment(cls, start: Position, end: Position, point: Position) -> bool:
        # UxV = |U| |V| sin(theta) = 0 if colinear
        # U.V = |U| |V| cos(theta) = |U| |V|= U.U |V|/|U|
        # Fixme: could cache
        U = end - start
        V = point - start
        return (math.fabs(U.vectorial_product(V)) < EPSILON
                and
                0 <= U.scalar_product(V) <= U.scalar_product(U))

####################################################################################################

class PositionAngle(Position):

    ##############################################

    def __init__(self, x: float, y: float, angle: int) -> None:
        super().__init__(x, y)
        self._angle = angle

    ##############################################

    @property
    def angle(self) -> int:
        return self._angle

    ##############################################

    def __str__(self) -> str:
        return super().__str__() + f" @{self._angle}"
