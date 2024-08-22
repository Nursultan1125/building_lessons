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

    LINE_LAYER_PATTERN = re.compile("B\s*(\d+)\s*H\s*(\d+)")
    E3DFACE_LAYER_PATTERN = re.compile("B\s*(\d+)\s*H\s*(\d+)")
    LAYER_PATTERN = re.compile("B+\d+\s+H+\d+")
    LINE_NUMBER_PATTERN = re.compile("H\s*(\d+)")
    E3DFACE_NUMBER_PATTERN = re.compile("H\s*(\d+)")

    def __post_init__(self):
        if self.is_valid():
            self.unique_name = " ".join([str(float(i)) for i in self.LINE_NUMBER_PATTERN.findall(self.name)[0]])
            return

        self.unique_name = self.name

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

    def to_tuple(self):
        return (self.x, self.y, self.z, self.layer)

    def __hash__(self):
        return hash((self.x, self.y, self.z))

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