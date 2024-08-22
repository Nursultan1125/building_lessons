import re
from dataclasses import dataclass
from functools import cached_property

from introduce.lesson02.dxf_parser import DXFParser
from introduce.lesson02.entities import Point, Line, E3DFace, Layer
from introduce.lesson03.consts import TEMPLATE


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

    def filter_by_layer_template(self):
        self.points = [p for p in self.points if p.layer.is_valid()]
        self.lines = [l for l in self.lines if l.layer.is_valid()]
        self.e3d_faces = [f for f in self.e3d_faces if f.layer.is_valid()]
        self.__dict__.pop("all_points", None)  # clear cache
        self.__dict__.pop("unique_points", None)  # clear cache
        self.__dict__.pop("layers", None)  # clear cache

    @cached_property
    def layers(self):
        layers = list({p.layer for p in self.unique_points.values()})
        return {l: i + 1 for i, l in enumerate(layers)}

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

    def export(self, filename) -> None:
        with open(filename, "w") as file:
            unique_points = ""
            drawing_objects = self.get_converted_lines()
            layers = ""
            for layer, i in self.layers.items():
                layers += f"{i} S0 3.06E6 {layer.unique_name}/\n"
            for point in self.unique_points.values():
                unique_points += f"{point.x} {point.y} {point.z}/\n"
            file.write(TEMPLATE.format(unique_points=unique_points, drawing_objects=drawing_objects, layers=layers))


if __name__ == "__main__":
    print("Parsing DXF")
    from datetime import datetime
    print(datetime.now())
    parser = DXFParser("data/lira_color11.dxf")
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
    lira.export("data/lira_color--out00.txt")
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
