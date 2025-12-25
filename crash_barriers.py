# crash_barriers.py
# Fully parametric crash barrier geometry
# Shape: Horizontal base -> Slope -> Vertical top (New Jersey type)

from OCC.Core.gp import gp_Pnt, gp_Vec, gp_Trsf, gp_Dir, gp_Ax2
from OCC.Core.BRepBuilderAPI import (
    BRepBuilderAPI_MakePolygon,
    BRepBuilderAPI_MakeFace,
    BRepBuilderAPI_Transform
)
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakePrism


# ------------------------------------------------------------
# Utility transforms
# ------------------------------------------------------------

def translate(shape, x=0, y=0, z=0):
    trsf = gp_Trsf()
    trsf.SetTranslation(gp_Vec(x, y, z))
    return BRepBuilderAPI_Transform(shape, trsf, True).Shape()


# ------------------------------------------------------------
# Crash barrier geometry - LEFT FACING (traffic side faces positive Y)
# ------------------------------------------------------------
def create_crash_barrier_left(
    length,
    width,
    height,
    base_width
):
    slope_height = 0.7 * height

    half_base = base_width / 2

    # Y positions (CENTERED)
    y_outer = -half_base           # outer bottom face (deck side)
    y_inner = +half_base           # traffic face

    # Top is inward
    y_top_inner = y_inner - (base_width - width)

    # Z positions
    z0 = 0.0
    z_slope_top = slope_height
    z_top = height

    # PROFILE (Y–Z)
    p1 = gp_Pnt(0, y_inner, z0)
    p2 = gp_Pnt(0, y_outer, z0)
    p3 = gp_Pnt(0, y_top_inner, z_slope_top)
    p4 = gp_Pnt(0, y_top_inner, z_top)
    p5 = gp_Pnt(0, y_inner, z_top)

    poly = BRepBuilderAPI_MakePolygon()
    for p in (p1, p2, p3, p4, p5):
        poly.Add(p)
    poly.Close()

    face = BRepBuilderAPI_MakeFace(poly.Wire()).Face()

    barrier = BRepPrimAPI_MakePrism(
        face,
        gp_Vec(length, 0, 0)
    ).Shape()

    return barrier


# ------------------------------------------------------------
# Crash barrier geometry - RIGHT FACING (traffic side faces negative Y)
# ------------------------------------------------------------
def create_crash_barrier_right(
    length,
    width,
    height,
    base_width
):
    slope_height = 0.7 * height

    half_base = base_width / 2

    # Y positions (CENTERED) - mirrored from left version
    y_outer = +half_base           # outer bottom face (deck side)
    y_inner = -half_base           # traffic face

    # Top is inward
    y_top_inner = y_inner + (base_width - width)

    # Z positions
    z0 = 0.0
    z_slope_top = slope_height
    z_top = height

    # PROFILE (Y–Z) - mirrored profile
    p1 = gp_Pnt(0, y_inner, z0)
    p2 = gp_Pnt(0, y_outer, z0)
    p3 = gp_Pnt(0, y_top_inner, z_slope_top)
    p4 = gp_Pnt(0, y_top_inner, z_top)
    p5 = gp_Pnt(0, y_inner, z_top)

    poly = BRepBuilderAPI_MakePolygon()
    for p in (p1, p2, p3, p4, p5):
        poly.Add(p)
    poly.Close()

    face = BRepBuilderAPI_MakeFace(poly.Wire()).Face()

    barrier = BRepPrimAPI_MakePrism(
        face,
        gp_Vec(length, 0, 0)
    ).Shape()

    return barrier


# ------------------------------------------------------------
# Placement
# ------------------------------------------------------------

def place_crash_barrier(shape, x, y, z):
    """
    Places crash barrier at position (x, y, z).
    """
    return translate(shape, x=x, y=y, z=z)