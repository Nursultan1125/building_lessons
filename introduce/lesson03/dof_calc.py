import math
from introduce.lesson02.entities import Point, Line, Layer, EntityType, E3DFace


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


def get_dof_points_from_faces_by_dof_line(faces: list[E3DFace], dof_line: Line) -> list[Point]:
    dof_points = []
    for face in faces:
        layer = Layer(name=dof_line.layer.name, type=EntityType.POINT)
        for point in face.points:
            if is_dof_point(dof_line, point):
                dof_points.append(Point(point.x, point.y, point.z, layer))
    return dof_points


def get_dof_points_from_faces_by_dof_lines(faces: list[E3DFace], dof_lines: list[Line]) -> list[Point]:
    dof_points = []
    for dof_line in dof_lines:
        dof_points.extend(get_dof_points_from_faces_by_dof_line(faces, dof_line))
    return dof_points


def get_dof_points_from_lines_by_dof_lines(lines: list[Line], dof_lines: list[Line]) -> list[Point]:
    dof_points = []
    for dof_line in dof_lines:
        dof_points.extend(get_dof_points_from_lines_by_dof_line(lines, dof_line))
    return dof_points


def triangle_area(point1: Point, point2: Point, point3: Point) -> float:
    a_length = distance(point1, point2)
    b_length = distance(point1, point3)
    c_length = distance(point2, point3)
    perimeter = (a_length + b_length + c_length) / 2
    return math.sqrt(perimeter * (perimeter - a_length) * (perimeter - b_length) * (perimeter - c_length))


def get_face_area(face: E3DFace) -> float:
    a_point = face.points[0]
    b_point = face.points[1]
    c_point = face.points[3]
    d_point = face.points[2]
    return triangle_area(a_point, b_point, c_point) + triangle_area(b_point, c_point, d_point)


def is_dof_point_with_3d_face(face: E3DFace, point: Point):
    face_area = get_face_area(face)
    a_point = face.points[0]
    b_point = face.points[1]
    c_point = face.points[3]
    d_point = face.points[2]
    area_triangles = (
        triangle_area(a_point, point, c_point) +
        triangle_area(a_point, point, b_point) +
        triangle_area(b_point, point, d_point) +
        triangle_area(c_point, point, d_point)
    )
    return abs(area_triangles - face_area) <= point.accuracy


def get_dof_points_from_lines_with_dof_3dface(lines: list[Line], dof_face: E3DFace) -> list[Point]:
    dof_points = []

    for line in lines:
        layer = Layer(name=dof_face.layer.name, type=EntityType.POINT)
        if is_dof_point_with_3d_face(dof_face, line.start):
            dof_points.append(Point(line.start.x, line.start.y, line.start.z, layer))
        if is_dof_point_with_3d_face(dof_face, line.end):
            dof_points.append(Point(line.end.x, line.end.y, line.end.z, layer))
    return dof_points


def get_dof_points_from_lines_with_dof_3d_faces(lines: list[Line], dof_faces: list[E3DFace]) -> list[Point]:
    dof_points = []
    for dof_face in dof_faces:
        dof_points.extend(get_dof_points_from_lines_with_dof_3dface(lines, dof_face))
    return dof_points


def get_dof_points_from_with_dof_3d_face(faces: list[E3DFace], dof_face: E3DFace) -> list[Point]:
    dof_points = []
    for face in faces:
        layer = Layer(name=dof_face.layer.name, type=EntityType.POINT)
        for point in face.points:
            if is_dof_point_with_3d_face(dof_face, point):
                dof_points.append(Point(point.x, point.y, point.z, layer))
    return dof_points


def get_dof_points_from_with_dof_3d_faces(faces: list[E3DFace], dof_faces: list[E3DFace]) -> list[Point]:
    dof_points = []
    for dof_face in dof_faces:
        dof_points.extend(get_dof_points_from_with_dof_3d_face(faces, dof_face))
    return dof_points
