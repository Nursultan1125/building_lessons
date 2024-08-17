import json


def dxf_to_json(dxf_file, json_file):
    faces = []
    current_face = None

    with open(dxf_file, 'r') as file:
        lines = file.readlines()

    iterator = iter(lines)
    entities_section = False

    for line in iterator:
        line = line.strip()

        if line == 'SECTION':
            next_line = next(iterator).strip()
            if next_line == '2':
                section_type = next(iterator).strip()
                if section_type == 'ENTITIES':
                    entities_section = True
                else:
                    entities_section = False

        if entities_section:
            if line == '0' and next(iterator).strip() == '3DFACE':
                next(iterator)
                next(iterator)
                if current_face is not None:
                    faces.append(current_face)
                current_face = []
            if line == '10':
                x = float(next(iterator).strip())
                next(iterator)
                y = float(next(iterator).strip())
                next(iterator)
                z = float(next(iterator).strip())
                current_face.append((x, y, z))
                # Repeat for the next points
            elif line == '11':
                x = float(next(iterator).strip())
                next(iterator)
                y = float(next(iterator).strip())
                next(iterator)
                z = float(next(iterator).strip())
                current_face.append((x, y, z))
            elif line == '12':
                x = float(next(iterator).strip())
                next(iterator)
                y = float(next(iterator).strip())
                next(iterator)
                z = float(next(iterator).strip())
                current_face.append((x, y, z))
            elif line == '13':
                x = float(next(iterator).strip())
                next(iterator)
                y = float(next(iterator).strip())
                next(iterator)
                z = float(next(iterator).strip())
                current_face.append((x, y, z))

    if current_face is not None:
        faces.append(current_face)

    json_content = {'faces': [{'points': face} for face in faces]}

    with open(json_file, 'w') as json_file:
        json.dump(json_content, json_file, indent=4)


def parse_3face():
    ...



dxf_to_json('house2.dxf', 'house.json')
