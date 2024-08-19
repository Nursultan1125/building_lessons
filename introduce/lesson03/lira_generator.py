from dataclasses import dataclass
from functools import cached_property

from introduce.lesson02.dxf_parser import DXFParser
from introduce.lesson02.entities import Point, Line, E3DFace
from introduce.lesson03.consts import TEMPLATE


@dataclass
class Lira:
    points: list[Point]
    lines: list[Line]
    e3d_faces: list[E3DFace]

    @cached_property
    def all_points(self) -> list[Point]:
        points = []

        for i, line in enumerate(self.lines):
            points.append(line.start)
            points.append(line.end)
        for i, e3d_face in enumerate(self.e3d_faces):
            points.extend(e3d_face.points)

        return self.points + points

    @cached_property
    def unique_points(self) -> dict[int, Point]:
        points = self.all_points
        unique_points = []
        for point in points:
            if point not in unique_points:
                unique_points.append(point)

        res = {}
        for i, point in enumerate(unique_points):
            res[i + 1] = point
        return res

    def get_index(self, point: Point):
        indexes = self.unique_points
        for index, p in indexes.items():
            if p == point:
                return index

    def get_converted_lines(self):
        results = ""
        for line in self.lines:
            results += "5 1 {x} {y}/\n".format(x=self.get_index(line.start), y=self.get_index(line.end))
        return results

    def write_to_file(self, filename) -> None:
        with open(filename, "w") as file:
            unique_points = ""
            drawing_objects = self.get_converted_lines()
            for point in self.unique_points.values():
                unique_points += f"{point.x} {point.y} {point.z}/\n"
            file.write(TEMPLATE.format(unique_points=unique_points, drawing_objects=drawing_objects))


if __name__ == "__main__":
    parser = DXFParser("data/Check-To-Tolerance.dxf")
    # parser = DXFParser("../lesson02/data/hw.dxf")
    entities = parser.parse()
    lira = Lira(
        points=entities["POINT"],
        lines=entities["LINE"],
        e3d_faces=entities["3DFACE"]
    )
    print(len(lira.all_points))
    print(len(lira.unique_points))
    lira.write_to_file("data/Check-To-Tolerance-out.txt")
    # for i, k in enumerate(lira.unique_points.keys()):
    #     print(i, k)
    #     assert k == i + 1
    # for k, v in lira.unique_points.items():
    #     print(v)
    # for k, v in entities.items():
    #     print(f"Entities of type {k}:")
    #     for entity in v:
    #         print("    ", entity.to_tuple())
