from introduce.lesson02.entities import E3DFace, Point, Line, DXFEntity


class DXFEntityParser:
    POINT_MAP = {
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

    def parse(self, current_data: dict[str, float]) -> DXFEntity:
        raise NotImplementedError


class PointParser(DXFEntityParser):

    def parse(self, current_data: dict[str, float]) -> Point:
        return Point(
            x=current_data.get("10", 0.0),
            y=current_data.get("20", 0.0),
            z=current_data.get("30", 0.0)
        )


class LineParser(DXFEntityParser):

    def parse(self, current_data: dict[str, float]) -> Line:
        return Line(
            start=Point(
                x=current_data.get("10", 0.0),
                y=current_data.get("20", 0.0),
                z=current_data.get("30", 0.0)
            ),
            end=Point(
                x=current_data.get("11", 0.0),
                y=current_data.get("21", 0.0),
                z=current_data.get("31", 0.0)
            )
        )


class E3DFaceParser(DXFEntityParser):
    E3DFACE_POINT_COUNT = 4

    def parse(self, current_data: dict[str, float]) -> E3DFace:

        return E3DFace([
            Point(x=current_data.get("10", 0.0), y=current_data.get("20", 0.0), z=current_data.get("30", 0.0)),
            Point(x=current_data.get("11", 0.0), y=current_data.get("21", 0.0), z=current_data.get("31", 0.0)),
            Point(x=current_data.get("12", 0.0), y=current_data.get("22", 0.0), z=current_data.get("32", 0.0)),
            Point(x=current_data.get("13", 0.0), y=current_data.get("23", 0.0), z=current_data.get("33", 0.0))
        ])


class DXFParser:
    dxf_lines: list[str] = []
    entities: dict[str, list[DXFEntity]] = {
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

    def parse(self) -> dict[str, list[DXFEntity]]:

        lines = self.dxf_lines
        current_entity = ""
        current_data = {}

        for line in lines:
            parts = line.strip()
            print(parts)
            if len(parts) != 2:
                continue
            code, value = parts
            if code == "0":
                parser = self.PARSER_MAP.get(current_entity, None)
                if parser is None:
                    continue
                entity = parser.parse(current_data)
                self.entities[current_entity].append(entity)
                current_entity = value
                current_data = {}
            else:
                try:
                    current_data[code] = float(value)
                except ValueError:
                    pass
        return self.entities


if __name__ == '__main__':
    parser = DXFParser("data/drawing1.dxf")
    entities = parser.parse()
    for k, v in entities.items():
        print(f"Entities of type {k}:")
        for entity in v:
            print("    ", entity.to_tuple())

