from typing import Optional, List

from llist import dllist
from Box import Box
from Vector2 import Vector2
from voronoi.Box import Intersection


class Site:
    def __init__(self, index: int, point: Vector2, face: Optional['Face'] = None):
        self.index = index
        self.point = point
        self.face = face


class Vertex:
    def __init__(self, point: Vector2):
        self.point = point
        self.list_node = None


class HalfEdge:
    def __init__(self):
        self.origin: Optional[Vertex] = None
        self.destination: Optional[Vertex] = None
        self.twin: Optional['HalfEdge'] = None
        self.incident_face: Optional['Face'] = None
        self.prev: Optional['HalfEdge'] = None
        self.next: Optional['HalfEdge'] = None
        self.list_node = None


class Face:
    def __init__(self, site: Optional[Site] = None):
        self.site = site
        self.outer_component: Optional[HalfEdge] = None


class VoronoiDiagram:
    def __init__(self, points: List[Vector2]):
        self._sites = list()
        self._faces = list()
        self._vertices = dllist()
        self._half_edges = dllist()
        for i in range(0, len(points)):
            self._sites.append(Site(
                i, points[i], None
            ))
            self._faces.append(
                Face(
                    self._sites[-1]
                )
            )
            self._sites[-1].face = self._faces[-1]

    def get_site(self, i: int) -> Site:
        return self._sites[i]

    def get_sites(self) -> 'List[Site]':
        return self._sites

    def get_sites_count(self) -> int:
        return len(self._sites)

    def get_face(self, i: int) -> Face:
        return self._faces[i]

    def get_vertices(self) -> 'dllist':
        return self._vertices

    def get_half_edges(self) -> 'dllist':
        return self._half_edges

    def intersect(self, box: Box) -> bool:
        error = False
        processed_half_edges = set()
        vertices_to_remove = set()

        for site in self._sites:
            half_edge: HalfEdge = site.face.outer_component
            inside = box.contains(half_edge.origin.point)
            outer_component_dirty = not inside
            incoming_half_edge = None  # First half edge coming in the box
            outgoing_half_edge = None  # Last half edge going out the box
            incoming_side = outgoing_side = Box.Side.LEFT

            while True:

                intersections = [Intersection(), Intersection()]
                intersections_count = box.get_intersections(
                    half_edge.origin.point,
                    half_edge.destination.point,
                    intersections
                )
                next_inside = box.contains(half_edge.destination.point)
                next_half_edge = half_edge.next

                if not inside and not next_inside:
                    if intersections_count == 0:
                        vertices_to_remove.add(half_edge.origin)
                        self._remove_half_edge(half_edge)
                    elif intersections_count == 2:
                        vertices_to_remove.add(half_edge.origin)
                        if half_edge.twin in processed_half_edges:
                            half_edge.origin = half_edge.twin.destination
                            half_edge.destination = half_edge.twin.origin
                        else:
                            half_edge.origin = self._create_vertex(intersections[0].point)
                            half_edge.destination = self._create_vertex(intersections[1].point)
                        if outgoing_half_edge is not None:
                            self._link(box, outgoing_half_edge, outgoing_side,
                                       half_edge, intersections[0].side)
                        if incoming_half_edge is None:
                            incoming_half_edge = half_edge
                            incoming_side = intersections[0].side
                        outgoing_half_edge = half_edge
                        outgoing_side = intersections[1].side
                        processed_half_edges.add(half_edge)
                    else:
                        error = True
                elif inside and not next_inside:
                    if intersections_count == 1:
                        if half_edge.twin in processed_half_edges:
                            half_edge.destination = half_edge.twin.origin
                        else:
                            half_edge.destination = self._create_vertex(intersections[0].point)
                        outgoing_half_edge = half_edge
                        outgoing_side = intersections[0].side
                        processed_half_edges.add(half_edge)
                    else:
                        error = True
                elif not inside and next_inside:
                    if intersections_count == 1:
                        vertices_to_remove.add(half_edge.origin)
                        if half_edge.twin in processed_half_edges:
                            half_edge.origin = half_edge.twin.destination
                        else:
                            half_edge.origin = self._create_vertex(intersections[0].point)
                        if outgoing_half_edge is not None:
                            self._link(box, outgoing_half_edge, outgoing_side,
                                       half_edge, intersections[0].side)
                        if incoming_half_edge is None:
                            incoming_half_edge = half_edge
                            incoming_side = intersections[0].side
                        processed_half_edges.add(half_edge)
                    else:
                        error = True

                half_edge = next_half_edge
                inside = next_inside
                if half_edge == site.face.outer_component:
                    break

            if outer_component_dirty and incoming_half_edge is not None:
                self._link(box, outgoing_half_edge, outgoing_side,
                           incoming_half_edge, incoming_side)

            if outer_component_dirty:
                site.face.outer_component = incoming_half_edge

        for vertex in vertices_to_remove:
            self._remove_vertex(vertex)

        return not error

    def _create_vertex(self, point: Vector2) -> Vertex:
        self._vertices.append(Vertex(point))
        self._vertices.last.value.list_node = self._vertices.last
        return self._vertices.last.value

    def _create_corner(self, box: Box, side: Box.Side) -> Optional[Vertex]:
        match side:
            case Box.Side.LEFT:
                return self._create_vertex(Vector2(box.left, box.top))
            case Box.Side.BOTTOM:
                return self._create_vertex(Vector2(box.left, box.bottom))
            case Box.Side.RIGHT:
                return self._create_vertex(Vector2(box.right, box.bottom))
            case Box.Side.TOP:
                return self._create_vertex(Vector2(box.right, box.top))
            case _:
                return None

    def _create_half_edge(self, face: Face) -> HalfEdge:
        self._half_edges.append(HalfEdge())
        self._half_edges.last.value.incident_face = face
        self._half_edges.last.value.list_node = self._half_edges.last
        if face.outer_component is None:
            face.outer_component = self._half_edges.last.value
        return self._half_edges.last.value

    def _link(self, box: Box, start: HalfEdge, start_side: Box.Side, end: HalfEdge, end_side: Box.Side):
        half_edge = start
        side = int(start_side)
        while side != int(end_side):
            side = (side + 1) % 4
            half_edge.next = self._create_half_edge(start.incident_face)
            half_edge.next.prev = half_edge
            half_edge.next.origin = half_edge.destination
            half_edge.next.destination = self._create_corner(box, Box.Side(side))
            half_edge = half_edge.next
        half_edge.next = self._create_half_edge(start.incident_face)
        half_edge.next.prev = half_edge
        end.prev = half_edge.next
        half_edge.next.next = end
        half_edge.next.origin = half_edge.destination
        half_edge.next.destination = end.origin

    def _remove_vertex(self, vertex: Vertex):
        self._vertices.remove(vertex.list_node)

    def _remove_half_edge(self, half_edge: HalfEdge):
        self._half_edges.remove(half_edge.list_node)


from enum import Enum, auto, IntEnum
from typing import Optional


class Arc:
    class Color(Enum):
        RED = auto()
        BLACK = auto()

    def __init__(self):
        self.parent: Optional['Arc'] = None
        self.left: Optional['Arc'] = None
        self.right: Optional['Arc'] = None

        self.site: Optional[Site] = None
        self.left_half_edge: Optional[HalfEdge] = None
        self.right_half_edge: Optional[HalfEdge] = None
        self.event: Optional['Event'] = None

        self.prev: Optional['Arc'] = None
        self.next: Optional['Arc'] = None

        self.color: Arc.Color = Arc.Color.RED

    def __repr__(self):
        return f"Arc(site_index={self.site.index if self.site else 'None'})"


class EventType(IntEnum):
    SITE = 0
    CIRCLE = 1


class Event:
    def __init__(self, site_or_y, point: Optional[Vector2] = None, arc: Optional[Arc] = None):
        if isinstance(site_or_y, Site):
            self.type = EventType.SITE
            self.y = site_or_y.point.y
            self.site: Optional[Site] = site_or_y
            self.point: Optional[Vector2] = None
            self.arc: Optional[Arc] = None
        else:
            self.type = EventType.CIRCLE
            self.y = site_or_y
            self.site = None
            self.point = point
            self.arc = arc

        self.index = -1

    def __lt__(self, other: 'Event') -> bool:
        return self.y < other.y

    def __repr__(self):
        if self.type == EventType.SITE:
            return f"S({self.site.index}, {self.y})"
        else:
            return f"C({self.arc}, {self.y}, {self.point})"
