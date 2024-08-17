import json

from introduce.lesson01.calculate_elemts import Point, Element, Obj


with open("data/input_data2.json", "r") as f:
    data = json.loads(f.read())

    elements = []
    for el_dict in data:
        number, points = list(el_dict.items())[0]
        points = [Point(float(point[0]), float(point[1])) for point in points]
        element = Element(points)
        elements.append(element)
    obj = Obj(elements=elements)
    obj.print_indexes()