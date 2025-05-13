from typing import Optional, Tuple, Mapping, List, Dict

from Box import Box
from Vector2 import Vector2
from BeachLine import Beachline
from PriorityQueue import PriorityQueue
from VoronoiDiagram import VoronoiDiagram, Vertex, HalfEdge, Event, Arc, Site
from voronoi.VoronoiDiagram import EventType


class LinkedVertex:
    prev_half_edge: Optional[HalfEdge]
    next_half_edge: Optional[HalfEdge]
    vertex: Optional[Vertex]

    def __init__(self, prev_half_edge=None, vertex=None, next_half_edge=None):
        self.prev_half_edge = prev_half_edge
        self.vertex = vertex
        self.next_half_edge = next_half_edge


class FortuneAlgorithm:
    _diagram: VoronoiDiagram
    _beachline: Beachline
    _events: PriorityQueue
    _beachline_y: float

    def __init__(self, points: list):
        self._diagram = VoronoiDiagram(points)
        self._beachline = Beachline()
        self._events = PriorityQueue()
        self._beachline_y = 0.0

    def construct(self):
        for i in range(self._diagram.get_sites_count()):
            self._events.push(Event(self._diagram.get_site(i)))

        # Обработка событий
        while not self._events.is_empty():
            event = self._events.pop()
            self._beachline_y = event.y
            if event.type == EventType.SITE:
                self._handle_site_event(event)
            else:
                self._handle_circle_event(event)

    def get_diagram(self) -> 'VoronoiDiagram':
        return self._diagram

    def _handle_site_event(self, event: Event):
        site = event.site

        # 1. Проверка: пуста ли beachline
        if self._beachline.is_empty():
            self._beachline.set_root(self._beachline.create_arc(site))
            return

        # 2. Найти дугу, над которой появляется сайт
        arc_to_break = self._beachline.locate_arc_above(site.point, self._beachline_y)
        self._delete_event(arc_to_break)
        # 3. Разделить дугу и вставить новую
        middle_arc = self._break_arc(arc_to_break, site)
        left_arc = middle_arc.prev
        right_arc = middle_arc.next

        # 4. Добавить новое ребро
        self._add_edge(left_arc, middle_arc)
        middle_arc.right_half_edge = middle_arc.left_half_edge
        right_arc.left_half_edge = left_arc.right_half_edge

        # 5. Проверка возможных circle-событий
        if not self._beachline.is_nil(left_arc.prev):
            self._add_event(left_arc.prev, left_arc, middle_arc)
        if not self._beachline.is_nil(right_arc.next):
            self._add_event(middle_arc, right_arc, right_arc.next)

    def _handle_circle_event(self, event: Event):
        point = event.point
        arc = event.arc

        # 1. Добавить вершину в диаграмму
        vertex = self._diagram._create_vertex(point)

        # 2. Удалить события, связанные с сайтами соседних дуг
        left_arc = arc.prev
        right_arc = arc.next
        self._delete_event(left_arc)
        self._delete_event(right_arc)

        # 3. Обновить beachline и диаграмму
        self._remove_arc(arc, vertex)

        # 4. Проверить и добавить новые circle-события
        if not self._beachline.is_nil(left_arc.prev):
            self._add_event(left_arc.prev, left_arc, right_arc)
        if not self._beachline.is_nil(right_arc.next):
            self._add_event(left_arc, right_arc, right_arc.next)

    def _break_arc(self, arc: Arc, site: Site):
        # 1. Создать новую дугу и разбить старую на 2
        middle_arc = self._beachline.create_arc(site)
        left_arc = self._beachline.create_arc(arc.site)
        left_arc.left_half_edge = arc.left_half_edge
        right_arc = self._beachline.create_arc(arc.site)
        right_arc.right_half_edge = arc.right_half_edge

        # 2. Вставить в beachline
        self._beachline.replace(arc, middle_arc)
        self._beachline.insert_before(middle_arc, left_arc)
        self._beachline.insert_after(middle_arc, right_arc)
        # 3. Вернуть новую дугу
        return middle_arc

    # Arcs
    def _remove_arc(self, arc: Arc, vertex: Vertex):
        # 1. Завершаем ребра
        self._set_destination(arc.prev, arc, vertex)
        self._set_destination(arc, arc.next, vertex)

        # 2. Соединяем ребра
        arc.left_half_edge.next = arc.right_half_edge
        arc.right_half_edge.prev = arc.left_half_edge

        # 3. Обновляем beachline
        self._beachline.remove(arc)

        # 4. Создаём новое ребро
        prev_half_edge = arc.prev.right_half_edge
        next_half_edge = arc.next.left_half_edge
        self._add_edge(arc.prev, arc.next)
        self._set_origin(arc.prev, arc.next, vertex)
        self._set_prev_half_edge(arc.prev.right_half_edge, prev_half_edge)
        self._set_prev_half_edge(next_half_edge, arc.next.left_half_edge)

    def _is_moving_right(self, left: Arc, right: Arc) -> bool:
        return left.site.point.y < right.site.point.y

    # Breakpoint logic
    def _get_initial_x(self, left: Arc, right: Arc, moving_right: bool) -> float:
        return left.site.point.x if moving_right else right.site.point.x

    def _add_edge(self, left: Arc, right: Arc):
        # 1. Создаем два новых полуребра
        left.right_half_edge = self._diagram._create_half_edge(left.site.face)
        right.left_half_edge = self._diagram._create_half_edge(right.site.face)

        # 2. Устанавливаем полуребра-'близнецы' (twin)
        left.right_half_edge.twin = right.left_half_edge
        right.left_half_edge.twin = left.right_half_edge

    # Edges
    def _set_origin(self, left: Arc, right: Arc, vertex: Vertex):
        left.right_half_edge.destination = vertex
        right.left_half_edge.origin = vertex

    def _set_destination(self, left: Arc, right: Arc, vertex: Vertex):
        left.right_half_edge.origin = vertex
        right.left_half_edge.destination = vertex

    def _set_prev_half_edge(self, prev: HalfEdge, next_: HalfEdge):
        prev.next = next_
        next_.prev = prev

    def _add_event(self, left: Arc, middle: Arc, right: Arc):
        # 1.
        y, convergence_point = self._compute_convergence_point(left.site.point, middle.site.point, right.site.point)

        # 2. Проверяем, находится ли точка ниже текущего уровня beachline
        is_below = y <= self._beachline_y

        # 3. Смотрим, куда движутся точки пересечений
        left_breakpoint_moving_right = self._is_moving_right(left, middle)
        right_breakpoint_moving_right = self._is_moving_right(middle, right)

        # 4. Получаем начальные координаты x для полурёбер
        left_initial_x = self._get_initial_x(left, middle, left_breakpoint_moving_right)
        right_initial_x = self._get_initial_x(middle, right, right_breakpoint_moving_right)

        # 5. Проверяем, удовлетворяют ли дуги условиям для добавления события
        is_valid = (
                           (left_breakpoint_moving_right and left_initial_x < convergence_point.x) or
                           (not left_breakpoint_moving_right and left_initial_x > convergence_point.x)
                   ) and (
                           (right_breakpoint_moving_right and right_initial_x < convergence_point.x) or
                           (not right_breakpoint_moving_right and right_initial_x > convergence_point.x)
                   )

        # 6. Если событие валидно и точка находится ниже, добавляем его в очередь событий
        if is_valid and is_below:
            event = Event(y, convergence_point, middle)
            middle.event = event
            self._events.push(event)

    # Events
    def _delete_event(self, arc: Arc):
        if arc.event is not None:
            self._events.remove(arc.event.index)
            arc.event = None

    def _compute_convergence_point(self, point1: Vector2, point2: Vector2, point3: Vector2) -> Tuple[float, Vector2]:

        v1 = (point1 - point2).orthogonal()
        v2 = (point2 - point3).orthogonal()

        delta = 0.5 * (point3 - point1)

        t = delta.det(v2) / v1.det(v2)

        center = 0.5 * (point1 + point2) + t * v1

        r = center.distance_to(point1)

        y = center.y - r

        return y, center

    def bound(self, box: Box) -> bool:
        # Расширяем box
        for vertex in self._diagram.get_vertices():
            box.left = min(vertex.point.x, box.left)
            box.bottom = min(vertex.point.y, box.bottom)
            box.right = max(vertex.point.x, box.right)
            box.top = max(vertex.point.y, box.top)

        # Retrieve all non-bounded half-edges from the beachline
        linked_vertices = []
        vertices: Dict[int, List[Optional[LinkedVertex]]] = {i: [None] * 8 for i in
                                                             range(self._diagram.get_sites_count())}

        if not self._beachline.is_empty():
            left_arc = self._beachline.get_leftmost_arc()
            right_arc = left_arc.next
            while not self._beachline.is_nil(right_arc):
                # Bound the edge
                direction = (left_arc.site.point - right_arc.site.point).orthogonal()
                origin = (left_arc.site.point + right_arc.site.point) * 0.5
                # Line-box intersection
                intersection = box.get_first_intersection(origin, direction)
                # Create a new vertex and end the half-edges
                vertex = self._diagram._create_vertex(intersection.point)
                self._set_destination(left_arc, right_arc, vertex)

                # Initialize pointers
                if left_arc.site.index not in vertices:
                    vertices[left_arc.site.index] = [None] * 8
                if right_arc.site.index not in vertices:
                    vertices[right_arc.site.index] = [None] * 8

                # Store the vertex on the boundaries
                linked_vertices.append(LinkedVertex(None, vertex, left_arc.right_half_edge))
                vertices[left_arc.site.index][2 * int(intersection.side) + 1] = linked_vertices[-1]
                linked_vertices.append(LinkedVertex(right_arc.left_half_edge, vertex, None))
                vertices[right_arc.site.index][2 * int(intersection.side)] = linked_vertices[-1]

                # Move to the next edge
                left_arc = right_arc
                right_arc = right_arc.next

        # Add corners
        for cell_vertices in vertices.values():
            for i in range(5):
                side = i % 4
                next_side = (side + 1) % 4
                # Add first corner
                if cell_vertices[2 * side] is None and cell_vertices[2 * side + 1] is not None:
                    prev_side = (side + 3) % 4
                    corner = self._diagram._create_corner(box, Box.Side(side))
                    linked_vertices.append(LinkedVertex(None, corner, None))
                    cell_vertices[2 * prev_side + 1] = linked_vertices[-1]
                    cell_vertices[2 * side] = linked_vertices[-1]
                # Add second corner
                elif cell_vertices[2 * side] is not None and cell_vertices[2 * side + 1] is None:
                    corner = self._diagram._create_corner(box, Box.Side(next_side))
                    linked_vertices.append(LinkedVertex(None, corner, None))
                    cell_vertices[2 * side + 1] = linked_vertices[-1]
                    cell_vertices[2 * next_side] = linked_vertices[-1]

        # Join the half-edges
        for i, cell_vertices in vertices.items():
            for side in range(4):
                if cell_vertices[2 * side] is not None:
                    # Link vertices
                    half_edge = self._diagram._create_half_edge(self._diagram.get_face(i))
                    half_edge.origin = cell_vertices[2 * side].vertex
                    half_edge.destination = cell_vertices[2 * side + 1].vertex
                    cell_vertices[2 * side].next_half_edge = half_edge
                    half_edge.prev = cell_vertices[2 * side].prev_half_edge
                    if cell_vertices[2 * side].prev_half_edge is not None:
                        cell_vertices[2 * side].prev_half_edge.next = half_edge
                    cell_vertices[2 * side + 1].prev_half_edge = half_edge
                    half_edge.next = cell_vertices[2 * side + 1].next_half_edge
                    if cell_vertices[2 * side + 1].next_half_edge is not None:
                        cell_vertices[2 * side + 1].next_half_edge.prev = half_edge

        return True
