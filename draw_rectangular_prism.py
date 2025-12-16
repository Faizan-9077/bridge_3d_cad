from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCC.Core.gp import gp_Trsf, gp_Vec
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Transform

def create_rectangular_prism(length, breadth, height):
    """
    X: -length/2 → +length/2
    Y: -breadth/2 → +breadth/2
    Z: 0 → height
    """

    box = BRepPrimAPI_MakeBox(length, breadth, height).Shape()

    trsf = gp_Trsf()
    trsf.SetTranslation(
        gp_Vec(-length/2, -breadth/2, 0)
    )

    return BRepBuilderAPI_Transform(box, trsf, True).Shape()
