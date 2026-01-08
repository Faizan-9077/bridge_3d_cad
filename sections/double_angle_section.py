# sections/double_angle_section.py

from OCC.Core.gp import gp_Trsf, gp_Vec, gp_Ax2, gp_Pnt, gp_Dir
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Fuse

from sections.angle_section import create_angle_section


def create_double_angle_section(
    length,
    leg_h,
    leg_w,
    thickness,
    connection_type="LONGER_LEG"
):
    """
    Double angle (⅃L) section.

    Geometry convention:
    - Length  : +X
    - Width   : ±Y
    - Height  : +Z
    - Origin  : bounding-box center

    connection_type:
    - LONGER_LEG  : longer legs connected back-to-back
    - SHORTER_LEG : shorter legs connected back-to-back
    """

    base = create_angle_section(length, leg_h, leg_w, thickness)

    # Mirror to form ⅃
    mirror = gp_Trsf()
    mirror.SetMirror(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 1, 0)))
    mirrored = BRepBuilderAPI_Transform(base, mirror, True).Shape()

    # Decide spacing
    if connection_type == "LONGER_LEG":
        offset = leg_h / 2
    elif connection_type == "SHORTER_LEG":
        offset = leg_w / 2
    else:
        raise ValueError("Invalid connection_type")

    # Translate symmetrically
    trsf_pos = gp_Trsf()
    trsf_pos.SetTranslation(gp_Vec(0, +offset, 0))

    trsf_neg = gp_Trsf()
    trsf_neg.SetTranslation(gp_Vec(0, -offset, 0))

    a1 = BRepBuilderAPI_Transform(base, trsf_pos, True).Shape()
    a2 = BRepBuilderAPI_Transform(mirrored, trsf_neg, True).Shape()

    return BRepAlgoAPI_Fuse(a1, a2).Shape()
