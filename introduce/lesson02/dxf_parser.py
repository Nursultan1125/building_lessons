from dataclasses import dataclass, field

from introduce.lesson02.entities import E3DFace, Point, Line, DXFEntity, Layer, EntityType


@dataclass
class Entities:
    points: list[Point] = field(default_factory=list)
    lines: list[Line] = field(default_factory=list)
    e3d_faces: list[E3DFace] = field(default_factory=list)


class DXFEntityParser:
    POINT_MAP = {
        "8": "layer",
        "10": "x",
        "20": "y",
        "30": "z",

        "11": "x",
        "21": "y",
        "31": "z",

        "12": "x",
        "22": "y",
        "32": "z",

        "13": "x",
        "23": "y",
        "33": "z",
    }

    def parse(self, index_line: int, dxf_lines: list[str]) -> DXFEntity:
        raise NotImplementedError


class PointParser(DXFEntityParser):

    def parse(self, index_line: int, dxf_lines: list[str]) -> Point:
        coordinates = {}
        for number in range(index_line + 1, len(dxf_lines)):
            dxf_line = dxf_lines[number].strip()
            next_line = dxf_lines[number + 1].strip()

            coordinate = self.POINT_MAP.get(dxf_line, None)
            if coordinate == "layer":
                coordinates[coordinate] = Layer(name=next_line, type=EntityType.LINE)
                continue
            if coordinate:
                coordinates[coordinate] = float(next_line)
            if len(coordinates) == 4:
                break
        return Point(**coordinates)


class LineParser(DXFEntityParser):

    def parse(self, index_line: int, dxf_lines: list[str]) -> Line:
        start_coordinates = {}
        end_coordinates = {}
        layer = Layer(name="0", type=EntityType.LINE)
        for i in range(index_line + 1, len(dxf_lines)):
            dxf_line = dxf_lines[i].strip()
            next_line = dxf_lines[i + 1].strip()

            if dxf_line in ("10", "20", "30"):
                coordinate = self.POINT_MAP.get(dxf_line, None)
                if coordinate:
                    start_coordinates[coordinate] = float(next_line)
            elif dxf_line in ("11", "21", "31"):
                coordinate = self.POINT_MAP.get(dxf_line, None)
                if coordinate:
                    end_coordinates[coordinate] = float(next_line)
            elif dxf_line == "8":
                layer = Layer(name=next_line, type=EntityType.LINE)
            if len(start_coordinates) + len(end_coordinates) == 6:
                break
        return Line(
            start=Point(layer=layer, **start_coordinates),
            end=Point(layer=layer, **end_coordinates),
            layer=layer,
        )


class E3DFaceParser(DXFEntityParser):
    E3DFACE_POINT_COUNT = 4

    def parse(self, index_line: int, dxf_lines: list[str]) -> E3DFace:
        points = {}
        layer = Layer(name="0", type=EntityType.E3DFACE)
        for i in range(index_line + 1, len(dxf_lines)):
            dxf_line = dxf_lines[i].strip()
            next_line = dxf_lines[i + 1].strip()
            coordinate = self.POINT_MAP.get(dxf_line, None)
            if coordinate == "layer":
                layer = Layer(name=next_line, type=EntityType.E3DFACE)
                continue
            if coordinate:
                points.setdefault(f"{dxf_line[1]}", {})[coordinate] = float(next_line)
                points.setdefault(f"{dxf_line[1]}", {})["layer"] = layer
            if len(points) == self.E3DFACE_POINT_COUNT and all([len(c) == 4 for c in points.values()]):
                break

        return E3DFace(points=[Point(**coordinates) for coordinates in points.values()], layer=layer)


class DXFParser:
    dxf_lines: list[str] = []
    entities: dict[str, list[DXFEntity | Point | Line | E3DFace]] = {
        "POINT": [],
        "LINE": [],
        "3DFACE": []
    }

    INCLUDED_ENTITIES = ["POINT", "LINE", "3DFACE"]

    PARSER_MAP: dict[str, DXFEntityParser] = {
        "POINT": PointParser(),
        "LINE": LineParser(),
        "3DFACE": E3DFaceParser()
    }

    def __init__(self, path: str):
        with open(path, "r") as f:
            self.dxf_lines = f.readlines()
            f.close()

    def parse(self) -> dict[str, list[DXFEntity | Point | Line | E3DFace]]:

        in_entities_section = False
        for i, line in enumerate(self.dxf_lines):
            line = line.strip()
            if line == "ENTITIES":
                in_entities_section = True
                continue

            if in_entities_section:
                if line == "ENDSEC":
                    break

            parser = self.PARSER_MAP.get(line)
            if parser is None:
                continue
            entity = parser.parse(i, self.dxf_lines)
            self.entities[line].append(entity)
        return self.entities


if __name__ == '__main__':
    parser = DXFParser("data/test.dxf")
    entities = parser.parse()
    for k, v in entities.items():
        print(f"Entities of type {k}:")
        for entity in v:
            print("    ", entity.to_tuple())

