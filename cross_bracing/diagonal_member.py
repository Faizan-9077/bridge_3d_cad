from OCC.Core.gp import gp_Pnt, gp_Vec, gp_Trsf, gp_Ax1, gp_Dir
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Transform

from sections.section_factory import create_section_solid
from sections.section_database import get_section_roll_angle




def create_diagonal_member(
    p1,
    p2,
    thickness,
    section_type="BOX",
    section_props=None,
    roll_sign=+1
):
    """
    Creates a diagonal member between p1 and p2.
    Geometry behavior is kept IDENTICAL to box implementation.
    """

    vec = gp_Vec(p1, p2)
    length = vec.Magnitude()

    # 1. CREATE GEOMETRY (SECTION-AGNOSTIC)

    solid = create_section_solid(
        section_type=section_type,
        length=length,
        thickness=thickness,
        section_props=section_props
    )


    # 2. ROTATE FROM +X TO TARGET VECTOR

    x_dir = gp_Dir(1, 0, 0)
    target_dir = gp_Dir(vec)
    axis_vec = gp_Vec(x_dir.Crossed(target_dir))
    angle = x_dir.Angle(target_dir)

    if axis_vec.Magnitude() > 1e-6:
        trsf_rot = gp_Trsf()
        trsf_rot.SetRotation(
            gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(axis_vec)),
            angle
        )
        solid = BRepBuilderAPI_Transform(solid, trsf_rot, True).Shape()


    # 2B. ROLL CONTROL (ANGLE + CHANNEL)

    roll_angle = get_section_roll_angle(
        section_type,
        member_role="diagonal",
        roll_sign=roll_sign
    )

    member_axis_dir = target_dir

    if abs(roll_angle) > 1e-6:
        roll_trsf = gp_Trsf()
        roll_trsf.SetRotation(
            gp_Ax1(gp_Pnt(0, 0, 0), member_axis_dir),
            roll_angle
        )
        solid = BRepBuilderAPI_Transform(solid, roll_trsf, True).Shape()


    # 3. TRANSLATE TO MIDPOINT

    mid = gp_Pnt(
        (p1.X() + p2.X()) / 2,
        (p1.Y() + p2.Y()) / 2,
        (p1.Z() + p2.Z()) / 2
    )

    trsf_trans = gp_Trsf()
    trsf_trans.SetTranslation(gp_Vec(mid.X(), mid.Y(), mid.Z()))

    return BRepBuilderAPI_Transform(solid, trsf_trans, True).Shape()


def create_diagonal_bracing_between_girders(
    x,
    y_left,
    y_right,
    girder_depth,
    flange_thickness,
    thickness,
    flange_width,
    section_type="BOX",
    section_props=None
):
    """
    Creates single diagonal bracing between two adjacent girders.
    """

    z_bottom = flange_thickness / 2
    z_top = girder_depth - flange_thickness / 2

    y_left_web = y_left + flange_width
    y_right_web = y_right

    p1 = gp_Pnt(x, y_left_web, z_bottom)
    p2 = gp_Pnt(x, y_right_web, z_top)

    return [
        create_diagonal_member(
            p1,
            p2,
            thickness,
            section_type=section_type,
            section_props=section_props
        )
    ]
