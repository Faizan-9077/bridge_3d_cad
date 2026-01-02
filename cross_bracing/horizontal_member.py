from OCC.Core.gp import gp_Trsf, gp_Vec, gp_Ax1, gp_Dir, gp_Pnt
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Transform


from sections.section_factory import create_section_solid
from sections.section_database import get_section_roll_angle

def create_horizontal_member_y(
    x,
    y_left_girder_left_edge,
    y_right_girder_left_edge,
    z,
    thickness,
    flange_width,
    section_type="BOX",
    section_props=None,
    roll_sign=+1
):
    y_start = y_left_girder_left_edge + flange_width
    y_end = y_right_girder_left_edge
    length = y_end - y_start
    y_mid = (y_start + y_end) / 2


    # 1. CREATE GEOMETRY (SECTION-AGNOSTIC, ALONG +X)

    solid = create_section_solid(
        section_type=section_type,
        length=length,
        thickness=thickness,
        section_props=section_props
    )


    # 2. ALIGN FROM X → Y (HORIZONTAL MEMBER AXIS)

    trsf_align = gp_Trsf()
    trsf_align.SetRotation(
        gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1)),  # rotate about Z
        1.5708
    )
    solid = BRepBuilderAPI_Transform(solid, trsf_align, True).Shape()


    # 2B. ROLL CONTROL (ANGLE + CHANNEL)

    roll_angle = get_section_roll_angle(
    section_type,
    member_role="horizontal",
    roll_sign=roll_sign
    )


    member_axis_dir = gp_Dir(0, 1, 0)

    if abs(roll_angle) > 1e-6:
        roll_trsf = gp_Trsf()
        roll_trsf.SetRotation(
            gp_Ax1(gp_Pnt(0, 0, 0), member_axis_dir),
            roll_angle
        )
        solid = BRepBuilderAPI_Transform(solid, roll_trsf, True).Shape()


    # 3. FINAL PLACEMENT

    trsf = gp_Trsf()
    trsf.SetTranslation(gp_Vec(x, y_mid, z))

    return BRepBuilderAPI_Transform(solid, trsf, True).Shape()
