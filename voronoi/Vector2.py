import math


class Vector2:
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y

    def __neg__(self):
        return Vector2(-self.x, -self.y)

    def __iadd__(self, other):
        self.x += other.x
        self.y += other.y
        return self

    def __isub__(self, other):
        self.x -= other.x
        self.y -= other.y
        return self

    def __imul__(self, t):
        self.x *= t
        self.y *= t
        return self

    def orthogonal(self):
        return Vector2(-self.y, self.x)

    def dot(self, other):
        return self.x * other.x + self.y * other.y

    def norm(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def distance_to(self, other):
        return (self - other).norm()

    def det(self, other):
        return self.x * other.y - self.y * other.x

    @staticmethod
    def from_array(array):
        return Vector2(array[0], array[1])

    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)

    def __mul__(self, t):
        return Vector2(self.x * t, self.y * t)

    def __rmul__(self, t):
        return self * t

    def __repr__(self):
        return f"({self.x}, {self.y})"
