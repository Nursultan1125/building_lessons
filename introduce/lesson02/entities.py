from __future__ import annotations
from dataclasses import dataclass


class DXFEntity:
    ...

    def to_tuple(self):
        return ()

    def to_dict(self):
        return {}


@dataclass
class Point(DXFEntity):
    x: float
    y: float
    z: float
    accuracy: float = 0.0

    def __eq__(self, other: Point):
        return (
                abs(self.x - other.x) <= self.accuracy
                and abs(self.y - other.y) <= self.accuracy
                and abs(self.z - other.z) <= self.accuracy
        )

    def to_tuple(self):
        return (self.x, self.y, self.z)

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

    def to_tuple(self):
        return (self.start.to_tuple(), self.end.to_tuple())

    def to_dict(self):
        return {
            "start": self.start.to_dict(),
            "end": self.end.to_dict()
        }


@dataclass
class E3DFace(DXFEntity):
    points: list[Point]

    def to_tuple(self):
        return tuple([point.to_tuple() for point in self.points])