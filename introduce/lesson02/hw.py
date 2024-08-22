from introduce.lesson02.dxf_parser import DXFParser

# parser = DXFParser("../lesson03/data/lira_color00.dxf")
parser = DXFParser("data/test.dxf")
entities = parser.parse()

with open("data/hw.txt", "w") as f:
    print("222")
    for k, v in entities.items():
        f.write(f"Entities of type {k}:\n")
        for entity in v:
            f.write(f"    {entity.to_tuple()}\n")