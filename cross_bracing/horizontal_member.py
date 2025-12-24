from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCC.Core.gp import gp_Trsf, gp_Vec
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Transform


def create_horizontal_member_y(
    x,
    y_left_girder_left_edge,
    y_right_girder_left_edge,
    z,
    thickness,
    flange_width
):
    y_start = y_left_girder_left_edge + flange_width
    y_end = y_right_girder_left_edge
    length = y_end - y_start
    y_mid = (y_start + y_end) / 2

    box = BRepPrimAPI_MakeBox(
        thickness,
        length,
        thickness
    ).Shape()

    trsf_center = gp_Trsf()
    trsf_center.SetTranslation(
        gp_Vec(-thickness / 2, -length / 2, -thickness / 2)
    )
    box = BRepBuilderAPI_Transform(box, trsf_center, True).Shape()

    trsf = gp_Trsf()
    trsf.SetTranslation(gp_Vec(x, y_mid, z))
    return BRepBuilderAPI_Transform(box, trsf, True).Shape()


def create_horizontal_bracing_between_girders(
    x,
    y_left_girder_left_edge,
    y_right_girder_left_edge,
    z,
    thickness,
    flange_width
):
    """
    Creates a single horizontal bracing member between two adjacent girders.
    """

    return create_horizontal_member_y(
        x,
        y_left_girder_left_edge,
        y_right_girder_left_edge,
        z,
        thickness,
        flange_width
    )