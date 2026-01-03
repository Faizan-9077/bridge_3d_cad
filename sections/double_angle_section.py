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

    - LONGER_LEG  : longer legs connected back-to-back
    - SHORTER_LEG : shorter legs connected back-to-back

    Inner faces are explicitly aligned → NO GAP possible.
    """


    # Base angle (L)
    base = create_angle_section(
        length=length,
        leg_h=leg_h,
        leg_w=leg_w,
        thickness=thickness
    )

 
    # Mirror about YZ plane
    mirror = gp_Trsf()
    mirror.SetMirror(
        gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 1, 0))
    )
    mirrored = BRepBuilderAPI_Transform(base, mirror, True).Shape()


    # Decide which leg is CONNECTED

    if connection_type == "LONGER_LEG":
        connected_leg = leg_h
    elif connection_type == "SHORTER_LEG":
        connected_leg = leg_w
    else:
        raise ValueError("Invalid connection_type")

    #  FORCE INNER FACES TO MEET AT Y = 0
    # Inner face of leg is always at:
    # (connected_leg / 2) - thickness
    inner_face_offset = (connected_leg / 2) - thickness

    # Vertical centering (unchanged, stable)
    z_shift = -(connected_leg / 2 + thickness / 2)

    # Apply transforms

    # Mirrored ⅃ → inner face to -Y
    trsf_m = gp_Trsf()
    trsf_m.SetTranslation(
        gp_Vec(0, -inner_face_offset, z_shift)
    )
    mirrored = BRepBuilderAPI_Transform(
        mirrored, trsf_m, True
    ).Shape()

    # Normal L → inner face to +Y
    trsf_n = gp_Trsf()
    trsf_n.SetTranslation(
        gp_Vec(0, inner_face_offset, z_shift)
    )
    normal = BRepBuilderAPI_Transform(
        base, trsf_n, True
    ).Shape()

    # Fuse → SINGLE solid
    return BRepAlgoAPI_Fuse(mirrored, normal).Shape()
