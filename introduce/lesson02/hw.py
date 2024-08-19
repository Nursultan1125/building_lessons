from introduce.lesson02.dxf_parser import DXFParser

parser = DXFParser("data/hw.dxf")
entities = parser.parse()

for k, v in entities.items():
    print(f"Entities of type {k}:")
    for entity in v:
        print("    ", entity.to_tuple())