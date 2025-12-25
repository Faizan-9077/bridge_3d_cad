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


def mirror_y(shape):
    """
    Mirrors shape across Y-Z plane (kept for future use)
    """
    trsf = gp_Trsf()
    trsf.SetMirror(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 1, 0)))
    return BRepBuilderAPI_Transform(shape, trsf, True).Shape()


# ------------------------------------------------------------
# Crash barrier geometry
# ------------------------------------------------------------
# crash_barriers.py
# Parametric New Jersey crash barrier
# Geometry based on standard drawing proportions

from OCC.Core.gp import gp_Pnt, gp_Vec, gp_Trsf, gp_Dir, gp_Ax2
from OCC.Core.BRepBuilderAPI import (
    BRepBuilderAPI_MakePolygon,
    BRepBuilderAPI_MakeFace,
    BRepBuilderAPI_Transform
)
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakePrism


# ------------------------------------------------------------
# Utility
# ------------------------------------------------------------

def translate(shape, x=0, y=0, z=0):
    trsf = gp_Trsf()
    trsf.SetTranslation(gp_Vec(x, y, z))
    return BRepBuilderAPI_Transform(shape, trsf, True).Shape()


# ------------------------------------------------------------
# Crash barrier geometry
# ------------------------------------------------------------

def create_crash_barrier(
    length,
    width,        # top width (USER INPUT)
    height,       # total height (USER INPUT)
    base_width    # bottom width (USER INPUT)
):
    """
    New Jersey crash barrier
    Controlled ONLY by:
    - width (top)
    - height (total)
    - base_width (bottom)
    """

    # -------------------------
    # Reference drawing height
    # -------------------------
    REF_HEIGHT = 900.0

    # -------------------------
    # Derived heights (scaled)
    # -------------------------
    bottom_vertical_height = (100.0 / REF_HEIGHT) * height
    slope_height           = (250.0 / REF_HEIGHT) * height
    top_vertical_height    = height - bottom_vertical_height - slope_height

    # -------------------------
    # Derived widths
    # -------------------------
    mid_width = base_width - 0.5 * (base_width - width)

    # -------------------------
    # Y positions (widths)
    # -------------------------
    y_traffic = 0.0
    y_base = base_width
    y_mid  = mid_width
    y_top  = width

    # -------------------------
    # Z positions (heights)
    # -------------------------
    z0 = 0.0
    z1 = bottom_vertical_height
    z2 = bottom_vertical_height + slope_height
    z3 = height

    # -------------------------
    # Profile (Y–Z plane)
    # Bottom horizontal -> inward slope -> top vertical
    # -------------------------
    p1 = gp_Pnt(0, y_traffic, z0)
    p2 = gp_Pnt(0, y_base, z0)

    p3 = gp_Pnt(0, y_base, z1)
    p4 = gp_Pnt(0, y_mid,  z2)

    p5 = gp_Pnt(0, y_top,  z3)
    p6 = gp_Pnt(0, y_traffic, z3)

    poly = BRepBuilderAPI_MakePolygon()
    for p in (p1, p2, p3, p4, p5, p6):
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

def place_crash_barrier(barrier, x=0, y=0, z=0, mirror=False):
    """
    Places crash barrier at given x, y, z coordinates

    NOTE:
    - mirror is kept for future use
    - For current bridge, mirror SHOULD NOT be used
    """
    if mirror:
        barrier = mirror_y(barrier)

    return translate(barrier, x, y, z)
