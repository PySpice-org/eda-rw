####################################################################################################
#
# KiCad-RW — Python library to read/write KiCad Sexpr file format
# Copyright (C) 2021 Fabrice SALVAIRE
# SPDX-License-Identifier: AGPL-3.0-or-later
#
####################################################################################################

__all__ = [
    'EuclidianMatrice',
    'Position',
    'PositionAngle',
    'Vector',
]

####################################################################################################

import math
from typing import Any

####################################################################################################

EPSILON = 1e-4  # numerical tolerance to match coordinate

####################################################################################################

type Matrix2D = tuple[tuple[int, int], tuple[int, int]]

class EuclidianMatrice:

    ##############################################

    @classmethod
    def identity(cls) -> Matrix2D:
        return ((1, 0),
                (0, 1))

    ##############################################

    @classmethod
    def rotation(cls, angle: int) -> Matrix2D:
        match angle:
            case 0:
                return cls.identity()
            case 90:
                return ((+0, 1),
                        (-1, 0))
            case 180:
                # mirror x and y
                return ((-1, 0),
                        (+0, -1))
            case 270:
                # 90 and mirror y
                return ((+0, 1),
                        (-1, 0))
            case _:
                raise NotImplementedError

    ##############################################

    @classmethod
    def x_mirror(cls, matrice: Matrix2D) -> Matrix2D:
        return ((-matrice[0][0], -matrice[0][1]),
                (+matrice[1][0], +matrice[1][1]))

    @classmethod
    def y_mirror(cls, matrice: Matrix2D) -> Matrix2D:
        return ((+matrice[0][0], +matrice[0][1]),
                (-matrice[1][0], -matrice[1][1]))

####################################################################################################

class Position:

    ##############################################

    def __init__(self, x: float, y: float) -> None:
        self._x = x
        self._y = y

    ##############################################

    @property
    def x(self) -> float:
        return self._x

    @property
    def y(self) -> float:
        return self._y

    ##############################################

    def __str__(self) -> str:
        return f"xy=({self._x:.2f}, {self._y:.2f})"

    ##############################################

    def __eq__(self, other: Any) -> bool:
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

    def __mul__(self, matrice: Matrix2D) -> Vector:
        x = matrice[0][0] * self._x + matrice[0][1] * self._y
        y = matrice[1][0] * self._x + matrice[1][1] * self._y
        return Vector(x, y)

####################################################################################################

class Vector(Position):

    ##############################################

    @property
    def is_vertical(self) -> bool:
        return math.fabs(self._x) < EPSILON

    @property
    def is_horizontal(self) -> bool:
        return math.fabs(self._y) < EPSILON

    ##############################################

    def scalar_product(self, vector) -> float:
        return self._x * vector.x + self._y * vector.y

    ##############################################

    def vectorial_product(self, vector) -> float:
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
