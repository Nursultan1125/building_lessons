from __future__ import annotations

import re
from dataclasses import dataclass


class DXFEntity:
    ...

    def to_tuple(self):
        return ()

    def to_dict(self):
        return {}


class EntityType:
    POINT = 0
    LINE = 1
    E3DFACE = 2


@dataclass
class Layer:
    name: str
    unique_name: str | None = None
    type: EntityType | None = EntityType.POINT

    LINE_LAYER_PATTERN = re.compile("\sB+\d+\s+H+\d+")
    E3DFACE_LAYER_PATTERN = re.compile("\sH\s*(\d+)")

    LINE_NUMBER_PATTERN = re.compile("B\s*(\d+)\s*H\s*(\d+)")
    E3DFACE_NUMBER_PATTERN = re.compile("H\s*(\d+)")

    def __post_init__(self):
        if not self.is_valid():
            self.unique_name = self.name
            return
        if self.type == EntityType.LINE:
            self.unique_name = " ".join([str(float(i)) for i in self.LINE_NUMBER_PATTERN.findall(self.name)[0]])
        elif self.type == EntityType.E3DFACE:
            self.unique_name = " ".join([str(int(i) / 100) for i in self.E3DFACE_NUMBER_PATTERN.findall(self.name)])

    def to_lira_format(self, index: int):
        if self.type == EntityType.LINE:
            return f"{index} S0 3.06E6 {self.unique_name}/\n"
        elif self.type == EntityType.E3DFACE:
            return f"{index} 3.06E6 0.2 {self.unique_name}/\n"
        return ""

    def __str__(self):
        return f"Layer({self.name})"

    def is_valid(self) -> bool:
        if self.type == EntityType.LINE:
            return bool(self.LINE_LAYER_PATTERN.findall(self.name))
        elif self.type == EntityType.E3DFACE:
            return bool(self.E3DFACE_LAYER_PATTERN.findall(self.name))
        return True

    def __hash__(self):
        return hash(self.unique_name)


@dataclass
class Point(DXFEntity):
    x: float
    y: float
    z: float
    layer: Layer
    accuracy: float = 0.005

    def __eq__(self, other: Point):
        return (
                abs(self.x - other.x) <= self.accuracy
                and abs(self.y - other.y) <= self.accuracy
                and abs(self.z - other.z) <= self.accuracy
        )

    def __hash__(self):
        return hash((self.x, self.y, self.z, self.layer))

    def to_tuple(self):
        return (self.x, self.y, self.z, self.layer)

    def to_dict(self):
        return {
            "x": self.x,
            "y": self.y,
            "z": self.z
        }


@dataclass
class Line(DXFEntity):
    start: Point
    end: Point
    layer: Layer

    def to_tuple(self):
        return (self.start.to_tuple(), self.end.to_tuple(), self.layer)

    def to_dict(self):
        return {
            "start": self.start.to_dict(),
            "end": self.end.to_dict(),
            "layer": self.layer,
        }


@dataclass
class E3DFace(DXFEntity):
    points: list[Point]
    layer: Layer

    def to_tuple(self):
        return tuple([point.to_tuple() for point in self.points])