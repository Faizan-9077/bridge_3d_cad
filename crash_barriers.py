# crash_barriers.py
# Fully parametric crash barrier geometry
# Shape:
# Base vertical (100 mm)
# Left side: single gentle slope (50 mm reduction till top)
# Right side: two slopes
#   - slope 1: 250 mm reduction till Z = 350
#   - slope 2: extra 50 mm reduction till full height

from OCC.Core.gp import gp_Pnt, gp_Vec, gp_Trsf, gp_Dir, gp_Ax2
from OCC.Core.BRepBuilderAPI import (
    BRepBuilderAPI_MakePolygon,
    BRepBuilderAPI_MakeFace,
    BRepBuilderAPI_Transform
)
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakePrism


# Utility transforms
def translate(shape, x=0, y=0, z=0):
    trsf = gp_Trsf()
    trsf.SetTranslation(gp_Vec(x, y, z))
    return BRepBuilderAPI_Transform(shape, trsf, True).Shape()


def mirror_y(shape):
    """
    Mirror shape about XZ plane (Y -> -Y)
    """
    trsf = gp_Trsf()
    trsf.SetMirror(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 1, 0)))
    return BRepBuilderAPI_Transform(shape, trsf, True).Shape()


# LEFT crash barrier (traffic on +Y side)

def create_crash_barrier_left(
    length,
    width,
    height,
    base_width
):
    """
    LEFT barrier geometry (as per discussion)

    Base vertical height      : 100 mm
    Left side slope           : 50 mm reduction till full height
    Right side slope part 1   : 250 mm reduction till Z = 350
    Right side slope part 2   : extra 50 mm till full height
    """

    # Fixed dimensions
    base_height = 100.0
    slope1_top_z = 350.0

    half_base = base_width / 2.0

    # Y positions

    # Base
    y_left_base  = -half_base
    y_right_base = +half_base

    # Left side (single slope)
    y_left_top = y_left_base + 50.0

    # Right side (two slopes)
    y_right_slope1 = y_right_base - 250.0
    y_right_top    = y_right_base - 300.0  # 250 + 50

    # Z positions
    z0 = 0.0
    z_base_top = base_height
    z_slope1_top = slope1_top_z
    z_top = height

    # Profile points (Y–Z plane)
    # Clockwise, starting bottom-right

    p1 = gp_Pnt(0, y_right_base, z0)            # bottom right
    p2 = gp_Pnt(0, y_left_base,  z0)            # bottom left

    p3 = gp_Pnt(0, y_left_base,  z_base_top)    # base left vertical
    p4 = gp_Pnt(0, y_left_top,   z_top)          # left gentle slope

    p5 = gp_Pnt(0, y_right_top,  z_top)          # right small slope end
    p6 = gp_Pnt(0, y_right_slope1, z_slope1_top) # right slope 1 end
    p7 = gp_Pnt(0, y_right_base, z_base_top)     # right base top

    # Build face

    poly = BRepBuilderAPI_MakePolygon()
    for p in (p1, p2, p3, p4, p5, p6, p7):
        poly.Add(p)
    poly.Close()

    face = BRepBuilderAPI_MakeFace(poly.Wire()).Face()

    # Extrude along X

    barrier = BRepPrimAPI_MakePrism(
        face,
        gp_Vec(length, 0, 0)
    ).Shape()


    return barrier

# RIGHT crash barrier (mirror of LEFT)

def create_crash_barrier_right(
    length,
    width,
    height,
    base_width
):
    left_barrier = create_crash_barrier_left(
        length=length,
        width=width,
        height=height,
        base_width=base_width
    )

    return mirror_y(left_barrier)


# Placement helper

def place_crash_barrier(shape, x, y, z):
    """
    Places crash barrier at position (x, y, z)
    """
    return translate(shape, x=x, y=y, z=z)
