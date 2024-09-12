import re
from dataclasses import dataclass
from functools import cached_property

from introduce.lesson02.dxf_parser import DXFParser
from introduce.lesson02.entities import Point, Line, E3DFace, Layer
from introduce.lesson03.consts import TEMPLATE

START = "(0/1;csv2lira/2;5/39; 1:'dead load';)(1/\n"
END = """)(6/1 16 3 1 1/)
(7/1 0.0 0.0 0.0 0.0 /)
(8/0 0 0 0 0 0 0/)
"""


@dataclass
class LiraExporter:
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
    def unique_points(self) -> dict[Point, int]:
        points = self.all_points
        unique_points = set(points)

        res = {}
        for i, point in enumerate(unique_points):
            res[point] = i + 1
        return res

    def get_index(self, point: Point):
        return self.unique_points[point]

    def filter_by_layer_template(self):
        self.points = [p for p in self.points if p.layer.is_valid()]
        self.lines = [l for l in self.lines if l.layer.is_valid()]
        self.e3d_faces = [f for f in self.e3d_faces if f.layer.is_valid()]
        self.__dict__.pop("all_points", None)  # clear cache
        self.__dict__.pop("unique_points", None)  # clear cache
        self.__dict__.pop("layers", None)  # clear cache

    @cached_property
    def layers(self):
        layers = list({p.layer for p in self.unique_points.keys()})
        return {l: i + 1 for i, l in enumerate(layers)}

    def convert_3d_face(self, face: E3DFace):
        face_type = 42 if face.is_triangle() else 44
        if face_type == 42:
            exported_points = [str(self.get_index(p)) for p in set(face.points)]
        else:
            exported_points = [
                str(self.get_index(p)) for p in [face.points[0], face.points[1], face.points[3], face.points[2]]
            ]
        return "{face_type} {layer} {points}/\n".format(
            face_type=face_type,
            layer=self.get_layer_index(face.layer),
            points=" ".join(exported_points),
        )

    def get_layer_index(self, layer: Layer):
        return self.layers[layer]

    def get_converted_lines(self):
        results = ""
        for line in self.lines:
            results += "5 {layer} {start} {end}/\n".format(
                start=self.get_index(line.start),
                end=self.get_index(line.end),
                layer=self.get_layer_index(line.layer)
            )
        return results

    def get_converted_e3d_faces(self):
        results = ""
        for face in self.e3d_faces:
            points = [str(self.get_index(p)) for p in face.points]
            results += "44 {layer} {points}/\n".format(
                layer=self.get_layer_index(face.layer),
                points=" ".join(points),
            )
        return results

    def export(self, filename) -> None:
        with open(filename, "w") as file:
            unique_points = ""
            drawing_objects = self.get_converted_lines()
            drawing_objects += "\n" + self.get_converted_e3d_faces()
            layers = ""
            for layer, i in self.layers.items():
                layers += layer.to_lira_format(i)
            for point in self.unique_points.keys():
                unique_points += f"{point.x} {point.y} {point.z}/\n"
            file.write(TEMPLATE.format(unique_points=unique_points, drawing_objects=drawing_objects, layers=layers))

    def export_partial(self, filename):
        """(0/1;csv2lira/2;5/39; 1:'dead load';)(1/
        {drawing_objects}
        )(3/
        {layers}
        (4/
        {unique_points}
        )(6/1 16 3 1 1/)
        (7/1 0.0 0.0 0.0 0.0 /)
        (8/0 0 0 0 0 0 0/)
        """
        with open(filename, "w") as file:
            file.write(START)
            for line in self.lines:
                file.write("5 {layer} {start} {end}/\n".format(
                    start=self.get_index(line.start),
                    end=self.get_index(line.end),
                    layer=self.get_layer_index(line.layer)
                ))
            for face in self.e3d_faces:
                file.write(self.convert_3d_face(face))
            file.write(")(3/\n")
            for layer, i in self.layers.items():
                file.write(layer.to_lira_format(i))
            file.write(")(4/\n")
            for point in self.unique_points.keys():
                file.write(f"{point.x} {point.y} {point.z}/\n")
            file.write(")(5/\n")
            for point in self.points:
                dof = point.layer.unique_name.replace("fx","4")
                dof = dof.replace("fy", "5")
                dof = dof.replace("fz", "6")
                dof = dof.replace("x", "1")
                dof = dof.replace("y", "2")
                dof = dof.replace("z", "3")

                file.write(f"{self.get_index(point)} {dof}/\n")
            file.write(END)


if __name__ == "__main__":
    print("Parsing DXF")
    from datetime import datetime

    print(datetime.now())
    parser = DXFParser("data/POINTS.dxf")
    # parser = DXFParser("data/DZ_6-exp4.dxf")
    # parser = DXFParser("../lesson02/data/hw.dxf")
    entities = parser.parse()
    print(datetime.now())
    print("Lira exporting")
    lira = LiraExporter(
        points=entities["POINT"],
        lines=entities["LINE"],
        e3d_faces=entities["3DFACE"]
    )
    # lira.export("data/layer-out-cache.txt")
    print(datetime.now())
    print("Filtering")
    lira.filter_by_layer_template()
    print(datetime.now())
    print("writing output")
    lira.export_partial("data/POINTS2.txt")
    print(datetime.now())
    print("Done")
    # print(len(lira.all_points))
    # print(len(lira.unique_points))
    # print("\n================================")
    # lira.filter_by_layer_template()
    # print(len(lira.all_points))
    # print(len(lira.unique_points))
    # lira.export("data/layer-out.txt")
    # # for i, k in enumerate(lira.unique_points.keys()):
    # #     print(i, k)
    # #     assert k == i + 1
    # # for k, v in lira.unique_points.items():
    # #     print(v)
    # for k, v in entities.items():
    #     print(f"Entities of type {k}:")
    #     for entity in v:
    #         print("    ", entity.to_tuple())
