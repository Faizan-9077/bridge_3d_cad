from OCC.Core.gp import gp_Pnt, gp_Vec, gp_Trsf, gp_Ax1, gp_Dir
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Transform


def create_diagonal_member(p1, p2, thickness):
    vec = gp_Vec(p1, p2)
    length = vec.Magnitude()

    box = BRepPrimAPI_MakeBox(
        length,
        thickness,
        thickness
    ).Shape()

    trsf_center = gp_Trsf()
    trsf_center.SetTranslation(
        gp_Vec(-length / 2, -thickness / 2, -thickness / 2)
    )
    box = BRepBuilderAPI_Transform(box, trsf_center, True).Shape()

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
    box = BRepBuilderAPI_Transform(box, trsf_rot, True).Shape()

    mid = gp_Pnt(
        (p1.X() + p2.X()) / 2,
        (p1.Y() + p2.Y()) / 2,
        (p1.Z() + p2.Z()) / 2
    )

    trsf_trans = gp_Trsf()
    trsf_trans.SetTranslation(gp_Vec(mid.X(), mid.Y(), mid.Z()))
    return BRepBuilderAPI_Transform(box, trsf_trans, True).Shape()


def create_diagonal_bracing_between_girders(
    x,
    y_left,
    y_right,
    girder_depth,
    flange_thickness,
    thickness,
    flange_width
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
        create_diagonal_member(p1, p2, thickness)
    ]




