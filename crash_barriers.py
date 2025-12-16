# crash_barrier.py
# Trapezoidal crash barrier geometry

from OCC.Core.gp import gp_Pnt, gp_Vec, gp_Trsf
from OCC.Core.BRepBuilderAPI import (
    BRepBuilderAPI_MakePolygon,
    BRepBuilderAPI_MakeFace,
    BRepBuilderAPI_Transform
)
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakePrism


def translate(shape, x=0, y=0, z=0):
    trsf = gp_Trsf()
    trsf.SetTranslation(gp_Vec(x, y, z))
    return BRepBuilderAPI_Transform(shape, trsf, True).Shape()


def create_crash_barrier(length, base_width, top_width, height):
    """
    Creates trapezoidal crash barrier extruded along X
    """

    # Trapezoidal profile in Y-Z plane
    p1 = gp_Pnt(0, -base_width / 2, 0)
    p2 = gp_Pnt(0,  base_width / 2, 0)
    p3 = gp_Pnt(0,  top_width / 2, height)
    p4 = gp_Pnt(0, -top_width / 2, height)

    poly = BRepBuilderAPI_MakePolygon()
    for p in (p1, p2, p3, p4):
        poly.Add(p)
    poly.Close()

    face = BRepBuilderAPI_MakeFace(poly.Wire()).Face()

    barrier = BRepPrimAPI_MakePrism(
        face,
        gp_Vec(length, 0, 0)
    ).Shape()

    return barrier


def place_crash_barrier(barrier, x=0, y=0, z=0):
    """
    Places crash barrier at given x, y, z
    """
    return translate(barrier, x, y, z)
