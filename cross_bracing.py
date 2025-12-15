# cross_bracing.py
# X-type cross bracing for steel girder bridge
# Stable, parametric, OCC-safe implementation

from OCC.Core.gp import gp_Pnt, gp_Vec, gp_Trsf, gp_Ax1, gp_Dir
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Transform
import math


# ------------------------------------------------------------
# Core function: diagonal bracing member
# ------------------------------------------------------------

def make_diagonal_member(p1, p2, thickness):
    """
    Creates a diagonal steel bracing member between two points.
    """

    # Vector from p1 to p2
    vec = gp_Vec(p1, p2)
    length = vec.Magnitude()

    if length < 1e-6:
        return None

    # 1. Create box along X-axis at origin
    box = BRepPrimAPI_MakeBox(length, thickness, thickness).Shape()

    # 2. Rotate box to align with p1 -> p2 direction
    x_dir = gp_Dir(1, 0, 0)
    target_dir = gp_Dir(vec)

    axis_vec = gp_Vec(x_dir.Crossed(target_dir))
    angle = x_dir.Angle(target_dir)

    trsf_rot = gp_Trsf()
    if axis_vec.Magnitude() > 1e-6:
        trsf_rot.SetRotation(
            gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(axis_vec)),
            angle
        )

    box = BRepBuilderAPI_Transform(box, trsf_rot).Shape()

    # 3. Translate box to starting point p1
    trsf_trans = gp_Trsf()
    trsf_trans.SetTranslation(gp_Vec(p1.X(), p1.Y(), p1.Z()))

    box = BRepBuilderAPI_Transform(box, trsf_trans).Shape()

    return box


# ------------------------------------------------------------
# X bracing between two adjacent girders
# ------------------------------------------------------------

def create_x_bracing_between_girders(
    x,
    y1,
    y2,
    girder_depth,
    thickness
):
    """
    Creates X-type cross bracing between two adjacent girders.
    """

    braces = []

    z_bottom = 0.0
    z_top = girder_depth

    # Diagonal /
    p1 = gp_Pnt(x, y1, z_bottom)
    p2 = gp_Pnt(x, y2, z_top)
    d1 = make_diagonal_member(p1, p2, thickness)

    # Diagonal \
    p3 = gp_Pnt(x, y1, z_top)
    p4 = gp_Pnt(x, y2, z_bottom)
    d2 = make_diagonal_member(p3, p4, thickness)

    if d1:
        braces.append(d1)
    if d2:
        braces.append(d2)

    return braces


# ------------------------------------------------------------
# Build cross bracing along entire bridge span
# ------------------------------------------------------------

def create_cross_bracing(
    span_length,
    girder_spacing,
    n_girders,
    girder_depth,
    bracing_spacing,
    thickness
):
    """
    Builds X-type cross bracing along the bridge span.
    """

    cross_bracings = []

    total_width = (n_girders - 1) * girder_spacing
    n_frames = int(span_length / bracing_spacing) + 1

    for i in range(n_frames):
        x = i * bracing_spacing

        for g in range(n_girders - 1):
            y1 = g * girder_spacing - total_width / 2
            y2 = (g + 1) * girder_spacing - total_width / 2

            cross_bracings.extend(
                create_x_bracing_between_girders(
                    x,
                    y1,
                    y2,
                    girder_depth,
                    thickness
                )
            )

    return cross_bracings
