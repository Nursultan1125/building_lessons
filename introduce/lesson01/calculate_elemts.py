from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Point:
    x: float
    y: float
    accuracy: float = 0.0

    def __eq__(self, other: Point):
        return abs(self.x - other.x) <= self.accuracy and abs(self.y - other.y) <= self.accuracy


@dataclass
class Element:
    points: list[Point]

    def get_indexes(self) -> list[Point]:
        results = []
        for point in self.points:
            if point not in results:
                results.append(point)
        return results


@dataclass
class Obj:
    elements: list[Element]
    _cache_indexes: dict[int, Point] | None = None

    def get_indexes(self) -> dict[int, Point]:
        points = []
        if self._cache_indexes is not None:
            return self._cache_indexes
        for i in self.elements:
            points += i.get_indexes()
        res = []
        for point in points:
            if point not in res:
                res.append(point)
        self._cache_indexes = {i + 1: p for i, p in enumerate(res)}
        return self._cache_indexes

    def get_index(self, point: Point):
        indexes = self.get_indexes()
        for index, p in indexes.items():
            if p == point:
                return index

    def convert_to_index_format(self):
        results = []
        for i, element in enumerate(self.elements):
            element_dict = {i + 1: []}
            for point in element.points:
                index = self.get_index(point)
                element_dict[i + 1].append(index)
            results.append(element_dict)
        return results

    def print_indexes(self):
        for index, point in self.get_indexes().items():
            print(index, "---", point)
        print(self.convert_to_index_format())


if __name__ == '__main__':
    element = Element(
        [
            Point(1, 1),
            Point(1.001, 2),
            Point(1, 2.004),
            Point(2, 2),
            Point(2, 1),
        ]
    )

    element2 = Element(
        [
            Point(1, 2),
            Point(1, 3),
            Point(3, 2),
            Point(2, 2),
        ]
    )
    obj = Obj([element, element2])
    print(obj.get_indexes())
    print(len(obj.get_indexes()))
