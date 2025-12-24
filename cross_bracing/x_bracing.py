from OCC.Core.gp import gp_Pnt
from .diagonal_member import create_diagonal_member
from .horizontal_member import create_horizontal_member_y


def create_x_bracing_between_girders(
    x,
    y_left,
    y_right,
    girder_depth,
    flange_thickness,
    thickness,
    flange_width,
    bracket_option
):
    braces = []

    # Web–flange junction levels
    z_bottom = flange_thickness / 2
    z_top = girder_depth - flange_thickness / 2

    # Web positions
    y_left_diagonal = y_left + flange_width
    y_right_diagonal = y_right

    # Diagonals
    p1 = gp_Pnt(x, y_left_diagonal, z_bottom)
    p2 = gp_Pnt(x, y_right_diagonal, z_top)
    p3 = gp_Pnt(x, y_left_diagonal, z_top)
    p4 = gp_Pnt(x, y_right_diagonal, z_bottom)

    d1 = create_diagonal_member(p1, p2, thickness)
    d2 = create_diagonal_member(p3, p4, thickness)

    braces.extend([d1, d2])

    # Bottom bracket
    if bracket_option in ("LOWER", "BOTH"):
        bottom_member = create_horizontal_member_y(
            x, y_left, y_right, z_bottom, thickness, flange_width
        )
        braces.append(bottom_member)

    # Top bracket
    if bracket_option in ("UPPER", "BOTH"):
        top_member = create_horizontal_member_y(
            x, y_left, y_right, z_top, thickness, flange_width
        )
        braces.append(top_member)

    return braces

