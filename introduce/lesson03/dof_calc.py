import math
from introduce.lesson02.entities import Point, Line, Layer, EntityType


def distance(p1: Point, p2: Point):
    return math.dist(p1.to_tuple(), p2.to_tuple())


def is_dof_point(line: Line, p2: Point):
    line_length = distance(line.start, line.end)
    start_and_point_length = distance(line.start, p2)
    end_and_length = distance(line.end, p2)
    return line_length == start_and_point_length + end_and_length


def get_dof_points_from_lines_by_dof_line(lines: list[Line], dof_line: Line) -> list[Point]:
    dof_points = []

    for line in lines:
        layer = Layer(name=dof_line.layer.name, type=EntityType.POINT)
        if is_dof_point(dof_line, line.start):
            dof_points.append(Point(line.start.x, line.start.y, line.start.z, layer))
        if is_dof_point(dof_line, line.end):
            dof_points.append(Point(line.end.x, line.end.y, line.end.z, layer))
    return dof_points


def get_dof_points_from_lines_by_dof_lines(lines: list[Line], dof_lines: list[Line]) -> list[Point]:
    dof_points = []
    for dof_line in dof_lines:
        dof_points.extend(get_dof_points_from_lines_by_dof_line(lines, dof_line))
    return dof_points
