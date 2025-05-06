import math

from VoronoiDiagram import Arc, Site
from Vector2 import Vector2


class Beachline:
    _root: Arc
    _nil: Arc

    def __init__(self):
        self._nil = Arc()
        self._root = self._nil
        self._nil.color = Arc.Color.BLACK

    def create_arc(self, site: Site) -> Arc:
        res = Arc()
        res.parent = self._nil
        res.left = self._nil
        res.right = self._nil
        res.site = site
        res.left_half_edge = None
        res.right_half_edge = None
        res.event = None
        res.prev = self._nil
        res.next = self._nil
        res.color = Arc.Color.RED
        return res

    def is_nil(self, x: Arc) -> bool:
        return x == self._nil

    def is_empty(self) -> bool:
        return self.is_nil(self._root)

    def set_root(self, x):
        self._root = x
        self._root.color = Arc.Color.BLACK

    def get_leftmost_arc(self) -> Arc:
        x = self._root
        while not self.is_nil(x.prev):
            x = x.prev
        return x

    def _compute_breakpoint(self, point1: Vector2, point2: Vector2, l: float) -> float:
        x1, y1, x2, y2 = point1.x, point1.y, point2.x, point2.y
        d1 = 1.0 / (2.0 * (y1 - l))
        d2 = 1.0 / (2.0 * (y2 - l))
        a = d1 - d2
        b = 2.0 * (x2 * d2 - x1 * d1)
        c = (y1 * y1 + x1 * x1 - l * l) * d1 - (y2 * y2 + x2 * x2 - l * l) * d2
        delta = b * b - 4.0 * a * c
        return (-b + math.sqrt(delta)) / (2.0 * a)

    def locate_arc_above(self, point: Vector2, l: float) -> Arc:
        node = self._root
        found = False
        while not found:
            breakpoint_left = -math.inf
            breakpoint_right = math.inf
            if not self.is_nil(node.prev):
                breakpoint_left = self._compute_breakpoint(node.prev.site.point, node.site.point, l)
            if not self.is_nil(node.next):
                breakpoint_right = self._compute_breakpoint(node.site.point, node.next.site.point, l)
            if point.x < breakpoint_left:
                node = node.left
            elif point.x > breakpoint_right:
                node = node.right
            else:
                found = True
        return node

    def insert_before(self, x: Arc, y: Arc):
        if self.is_nil(x.left):
            x.left = y
            y.parent = x
        else:
            x.prev.right = y
            y.parent = x.prev
        y.prev = x.prev
        if not self.is_nil(y.prev):
            y.prev.next = y
        y.next = x
        x.next = y
        self._insert_fixup(y)

    def insert_after(self, x: Arc, y: Arc):
        if self.is_nil(x.right):
            x.right = y
            y.parent = x
        else:
            x.next.left = y
            y.parent = x.next
        y.next = x.next
        if not self.is_nil(y.next):
            y.next.prev = y
        y.prev = x
        x.next = y
        self._insert_fixup(y)

    def replace(self, x: Arc, y: Arc):
        self._transplant(x, y)
        y.left = x.left
        y.right = x.right
        if not self.is_nil(y.left):
            y.left.parent = y
        if not self.is_nil(y.right):
            y.right.parent = y
        y.prev = x.prev
        y.next = x.next
        if not self.is_nil(y.prev):
            y.prev.next = y
        if not self.is_nil(y.next):
            y.next.prev = y
        y.color = x.color

    def remove(self, z: Arc):
        y = z
        y_original_color = y.color
        if self.is_nil(z.left):
            x = z.right
            self._transplant(z, z.right)
        elif self.is_nil(z.right):
            x = z.left
            self._transplant(z, z.left)
        else:
            y = self._minimum(z.right)
            y_original_color = y.color
            x = y.right
            if y.parent == z:
                x.parent = y  # Because x could be Nil
            else:
                self._transplant(y, y.right)
                y.right = z.right
                y.right.parent = y
            self._transplant(z, y)
            y.left = z.left
            y.left.parent = y
            y.color = z.color
        if y_original_color == Arc.Color.BLACK:
            self._remove_fixup(x)
        if not self.is_nil(z.prev):
            z.prev.next = z.next
        if not self.is_nil(z.next):
            z.next.prev = z.prev

    def _minimum(self, x: Arc) -> Arc:
        while not self.is_nil(x.left):
            x = x.left
        return x

    def _transplant(self, u: Arc, v: Arc):
        if self.is_nil(u.parent):
            self.root = v
        elif u == u.parent.left:
            u.parent.left = v
        else:
            u.parent.right = v
        v.parent = u.parent

    def _insert_fixup(self, z: Arc):
        while z.parent.color == Arc.Color.RED:
            if z.parent == z.parent.parent.left:
                y = z.parent.parent.right
                # Case 1
                if y.color == Arc.Color.RED:
                    z.parent.color = Arc.Color.BLACK
                    y.color = Arc.Color.BLACK
                    z.parent.parent.color = Arc.Color.RED
                    z = z.parent.parent
                else:
                    # Case 2
                    if z == z.parent.right:
                        z = z.parent
                        self._left_rotate(z)
                    # Case 3
                    z.parent.color = Arc.Color.BLACK
                    z.parent.parent.color = Arc.Color.RED
                    self._right_rotate(z.parent.parent)
            else:
                y = z.parent.parent.left
                # Case 1
                if y.color == Arc.Color.RED:
                    z.parent.color = Arc.Color.BLACK
                    y.color = Arc.Color.BLACK
                    z.parent.parent.color = Arc.Color.RED
                    z = z.parent.parent
                else:
                    # Case 2
                    if z == z.parent.left:
                        z = z.parent
                        self._right_rotate(z)
                    # Case 3
                    z.parent.color = Arc.Color.BLACK
                    z.parent.parent.color = Arc.Color.RED
                    self._left_rotate(z.parent.parent)
        self.root.color = Arc.Color.BLACK

    def _remove_fixup(self, x: Arc):
        while x != self.root and x.color == Arc.Color.BLACK:
            if x == x.parent.left:
                w = x.parent.right
                # Case 1
                if w.color == Arc.Color.RED:
                    w.color = Arc.Color.BLACK
                    x.parent.color = Arc.Color.RED
                    self._left_rotate(x.parent)
                    w = x.parent.right
                # Case 2
                if w.left.color == Arc.Color.BLACK and w.right.color == Arc.Color.BLACK:
                    w.color = Arc.Color.RED
                    x = x.parent
                else:
                    # Case 3
                    if w.right.color == Arc.Color.BLACK:
                        w.left.color = Arc.Color.BLACK
                        w.color = Arc.Color.RED
                        self._right_rotate(w)
                        w = x.parent.right
                    # Case 4
                    w.color = x.parent.color
                    x.parent.color = Arc.Color.BLACK
                    w.right.color = Arc.Color.BLACK
                    self._left_rotate(x.parent)
                    x = self.root
            else:
                w = x.parent.left
                # Case 1
                if w.color == Arc.Color.RED:
                    w.color = Arc.Color.BLACK
                    x.parent.color = Arc.Color.RED
                    self._right_rotate(x.parent)
                    w = x.parent.left
                # Case 2
                if w.right.color == Arc.Color.BLACK and w.left.color == Arc.Color.BLACK:
                    w.color = Arc.Color.RED
                    x = x.parent
                else:
                    # Case 3
                    if w.left.color == Arc.Color.BLACK:
                        w.right.color = Arc.Color.BLACK
                        w.color = Arc.Color.RED
                        self._left_rotate(w)
                        w = x.parent.left
                    # Case 4
                    w.color = x.parent.color
                    x.parent.color = Arc.Color.BLACK
                    w.left.color = Arc.Color.BLACK
                    self._right_rotate(x.parent)
                    x = self.root
        x.color = Arc.Color.BLACK

    def _left_rotate(self, x: Arc):
        y = x.right
        x.right = y.left
        if not self.is_nil(y.left):
            y.left.parent = x
        y.parent = x.parent
        if self.is_nil(x.parent):
            self.root = y
        elif x == x.parent.left:
            x.parent.left = y
        else:
            x.parent.right = y
        y.left = x
        x.parent = y

    def _right_rotate(self, y: Arc):
        x = y.left
        y.left = x.right
        if not self.is_nil(x.right):
            x.right.parent = y
        x.parent = y.parent
        if self.is_nil(y.parent):
            self.root = x
        elif y == y.parent.left:
            y.parent.left = x
        else:
            y.parent.right = x
        x.right = y
        y.parent = x

    def arc_str(self, arc: Arc, tabs: str = '') -> str:
        result = f"{tabs}{arc.site.index} {arc.left_half_edge} {arc.right_half_edge}\n"
        if not self.is_nil(arc.left):
            result += self.arc_str(arc.left, tabs + '\t')
        if not self.is_nil(arc.right):
            result += self.arc_str(arc.right, tabs + '\t')
        return result

    def __str__(self):
        result = []
        arc = self.get_leftmost_arc()
        while not self.is_nil(arc):
            result.append(str(arc.site.index))
            arc = arc.next
        return ' '.join(result)
