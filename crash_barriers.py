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


def create_crash_barrier_left(
    length,
    width,       
    height,      
    base_width   
):
   

    # Heights (mm)
    base_h = 100.0
    slope1_end_z = 325.0      # end of first gentle slope
    slope2_start_z = 325.0    # start of final slope

    # Z levels
    z0 = 0.0
    z1 = base_h
    z2 = slope1_end_z
    z3 = slope2_start_z
    z4 = height

    # Bottom width
    y_left_base  = -base_width / 2.0
    y_right_base =  base_width / 2.0

    # Top width 
    y_left_top  = -width / 2.0
    y_right_top =  width / 2.0

    # Intermediate width = 250
    mid_width = 250.0
    y_right_mid =  mid_width / 2.0

    # Profile points (YZ plane)
    # Clockwise
    p1 = gp_Pnt(0, y_right_base, z0)   # bottom right
    p2 = gp_Pnt(0, y_left_base,  z0)   # bottom left

    p3 = gp_Pnt(0, y_left_base,  z1)   # base vertical (left)
    p4 = gp_Pnt(0, y_left_top,   z4)   # left gentle slope

    p5 = gp_Pnt(0, y_right_top,  z4)   # top right
    p6 = gp_Pnt(0, y_right_mid,  z3)   # start final slope
    p7 = gp_Pnt(0, y_right_mid,  z2) 
    p8 = gp_Pnt(0, y_right_base, z1)   # base vertical (right)

    # Build face
    poly = BRepBuilderAPI_MakePolygon()
    for p in (p1, p2, p3, p4, p5, p6, p7, p8):
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
