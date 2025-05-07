import math
from enum import Enum, auto, IntEnum
from typing import List, Optional
from Vector2 import Vector2


class Intersection:
    def __init__(self, side: Optional['Box.Side'] = None, point: Optional['Vector2'] = None):
        self.side = side
        self.point = point


class Box:
    EPSILON = 1e-9

    class Side(IntEnum):
        LEFT = 0
        BOTTOM = 1
        RIGHT = 2
        TOP = 3

    def __init__(self, left: float, bottom: float, right: float, top: float):
        self.left = left
        self.bottom = bottom
        self.right = right
        self.top = top

    def contains(self, point: 'Vector2') -> bool:
        return self.left - self.EPSILON <= point.x <= self.right + self.EPSILON \
            and self.bottom - self.EPSILON <= point.y <= self.top + self.EPSILON

    def get_first_intersection(self, origin: 'Vector2', direction: 'Vector2') -> 'Intersection':
        intersection = Intersection()
        t = math.inf
        if direction.x > 0.0:
            t = (self.right - origin.x) / direction.x
            intersection.side = Box.Side.RIGHT
            intersection.point = origin + t * direction
        elif direction.x < 0.0:
            t = (self.left - origin.x) / direction.x
            intersection.side = Box.Side.LEFT
            intersection.point = origin + t * direction
        if direction.y > 0.0:
            t_by_y = (self.top - origin.y) / direction.y
            if t_by_y < t:
                intersection.side = Box.Side.TOP
                intersection.point = origin + t_by_y * direction
        elif direction.y < 0.0:
            t_by_y = (self.bottom - origin.y) / direction.y
            if t_by_y < t:
                intersection.side = Box.Side.BOTTOM
                intersection.point = origin + t_by_y * direction
        return intersection

    def get_intersections(self, origin: 'Vector2', destination: 'Vector2', intersections: List['Intersection']) \
            -> int:
        direction = destination - origin
        t = [0.0, 0.0]
        i = 0
        if (origin.x < self.left - self.EPSILON or destination.x < self.left - self.EPSILON) and abs(
                direction.x) > self.EPSILON:
            t[i] = (self.left - origin.x) / direction.x
            if self.EPSILON < t[i] < 1.0 - self.EPSILON:
                intersections[i].side = Box.Side.LEFT
                intersections[i].point = origin + t[i] * direction
                if self.bottom - self.EPSILON <= intersections[i].point.y <= self.top + self.EPSILON:
                    i += 1

        if (origin.x > self.right + self.EPSILON or destination.x > self.right + self.EPSILON) and abs(
                direction.x) > self.EPSILON:
            t[i] = (self.right - origin.x) / direction.x
            if self.EPSILON < t[i] < 1.0 - self.EPSILON:
                intersections[i].side = Box.Side.RIGHT
                intersections[i].point = origin + t[i] * direction
                if self.bottom - self.EPSILON <= intersections[i].point.y <= self.top + self.EPSILON:
                    i += 1

        if (origin.y < self.bottom - self.EPSILON or destination.y < self.bottom - self.EPSILON) and abs(
                direction.y) > self.EPSILON:
            t[i] = (self.bottom - origin.y) / direction.y
            if i < 2 and self.EPSILON < t[i] < 1.0 - self.EPSILON:
                intersections[i].side = Box.Side.BOTTOM
                intersections[i].point = origin + t[i] * direction
                if self.left - self.EPSILON <= intersections[i].point.x <= self.right + self.EPSILON:
                    i += 1

        if (origin.y > self.top + self.EPSILON or destination.y > self.top + self.EPSILON) and abs(
                direction.y) > self.EPSILON:
            t[i] = (self.top - origin.y) / direction.y
            if i < 2 and self.EPSILON < t[i] < 1.0 - self.EPSILON:
                intersections[i].side = Box.Side.TOP
                intersections[i].point = origin + t[i] * direction
                if self.left - self.EPSILON <= intersections[i].point.x <= self.right + self.EPSILON:
                    i += 1

        if i == 2 and t[0] > t[1]:
            intersections[0], intersections[1] = intersections[1], intersections[0]

        return i
