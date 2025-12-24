# crash_barriers.py
# Fully parametric crash barrier geometry

from OCC.Core.gp import gp_Pnt, gp_Vec, gp_Trsf, gp_Dir, gp_Ax2
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

def mirror_y(shape):
    """
    Mirrors shape across Y-Z plane (flips along Y-axis)
    """
    trsf = gp_Trsf()
    trsf.SetMirror(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 1, 0)))
    return BRepBuilderAPI_Transform(shape, trsf, True).Shape()

def create_crash_barrier(
    length,
    base_width,
    toe_height,
    slope_height,
    top_vertical_height,
    mid_width_ratio,
    top_width
):
    """
    Parametric crash barrier profile (in Y-Z plane):
    
    Cross-section geometry:
    - Starts at traffic side (y=0, z=0)
    - Horizontal base extends to base_width
    - Vertical toe rises to toe_height
    - Slope section tapers inward to top_width
    - Top vertical section rises immediately from end of slope with constant width (top_width)
    
    Parameters:
    - length: barrier length along X-axis (mm)
    - base_width: width of horizontal base (mm)
    - toe_height: height of vertical toe section (mm)
    - slope_height: height of sloped section (mm)
    - top_vertical_height: height of top vertical section (mm)
    - mid_width_ratio: NOT USED - kept for compatibility
    - top_width: width of top vertical section (mm)
    """

    # Calculate Y positions (widths at different heights)
    y_traffic = 0.0                                    # Traffic side
    y_base = base_width                                # Base width
    y_top = top_width                                  # Top section width (slope ends here)

    # Calculate Z positions (heights)
    z_base = 0.0                                       # Ground level
    z_toe_top = toe_height                             # Top of toe section
    z_slope_top = toe_height + slope_height            # Top of slope (where vertical begins)
    z_top = toe_height + slope_height + top_vertical_height  # Final height

    # Define profile points in Y-Z plane (counterclockwise from traffic side)
    p1 = gp_Pnt(0, y_traffic, z_base)      # Traffic side bottom
    p2 = gp_Pnt(0, y_base, z_base)         # Base back corner
    p3 = gp_Pnt(0, y_base, z_toe_top)      # Top of toe section
    p4 = gp_Pnt(0, y_top, z_slope_top)     # Top of slope (vertical begins here)
    p5 = gp_Pnt(0, y_top, z_top)           # Top of barrier
    p6 = gp_Pnt(0, y_traffic, z_top)       # Traffic side top
    
    # Build closed polygon wire
    poly = BRepBuilderAPI_MakePolygon()
    for p in (p1, p2, p3, p4, p5, p6):
        poly.Add(p)
    poly.Close()

    # Create face from wire
    face = BRepBuilderAPI_MakeFace(poly.Wire()).Face()

    # Extrude along X-axis to create 3D barrier
    barrier = BRepPrimAPI_MakePrism(
        face,
        gp_Vec(length, 0, 0)
    ).Shape()

    return barrier


def place_crash_barrier(barrier, x=0, y=0, z=0, mirror=False):
    """
    Places crash barrier at given x, y, z coordinates
    
    Parameters:
    - barrier: the barrier shape to place
    - x, y, z: translation coordinates (mm)
    - mirror: if True, mirrors the barrier across Y-Z plane
    """
    if mirror:
        barrier = mirror_y(barrier)
    return translate(barrier, x, y, z)