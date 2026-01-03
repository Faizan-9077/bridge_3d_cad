from OCC.Core.gp import gp_Pnt
from .diagonal_member import create_diagonal_member
from .horizontal_member import create_horizontal_member_y


def create_k_bracing_between_girders(
    x,
    y_left,
    y_right,
    girder_depth,
    flange_thickness,
    thickness,
    flange_width,
    top_bracket=False, # Bottom bracket is mandatory; top is optional
    section_type="BOX",
    section_props=None,
    roll_sign = +1
):
    """
    Creates K-type cross bracing between two adjacent girders.

    Geometry rules (fixed):
        - Two diagonals meet at the midpoint of the bottom chord
        - Bottom horizontal bracket is ALWAYS present
        - Top horizontal bracket is OPTIONAL (top_bracket flag)

    Args:
        x: X-position along bridge span
        y_left: Y-coordinate of LEFT girder's LEFT edge (flange start)
        y_right: Y-coordinate of RIGHT girder's LEFT edge (flange start)
        girder_depth: Total depth of girder
        flange_thickness: Thickness of flanges
        thickness: Thickness of bracing members
        flange_width: Width (breadth) of girder flange
        top_bracket: If True, add top horizontal bracket
    """

    braces = []

    # Web–flange junction levels
    z_bottom = flange_thickness / 2
    z_top = girder_depth - flange_thickness / 2

    # Web positions
    y_left_diagonal = y_left + flange_width
    y_right_diagonal = y_right

    # Midpoint of bottom chord (horizontal)
    y_mid = (y_left_diagonal + y_right_diagonal) / 2

    # Diagonals (MANDATORY)

    # Left diagonal: left girder (top) → midpoint (bottom)
    p1 = gp_Pnt(x, y_left_diagonal, z_top)
    p2 = gp_Pnt(x, y_mid, z_bottom)
    d1 = create_diagonal_member(
        p1,
        p2,
        thickness,
        section_type=section_type,
        section_props=section_props,
        roll_sign = 1
    )

    # Right diagonal: right girder (top) → midpoint (bottom)
    p3 = gp_Pnt(x, y_right_diagonal, z_top)
    p4 = gp_Pnt(x, y_mid, z_bottom)
    d2 = create_diagonal_member(
        p3,
        p4,
        thickness,
        section_type=section_type,
        section_props=section_props,
        roll_sign = 0

    )

    braces.extend([d1, d2])


    # Bottom bracket (MANDATORY)

    bottom_member = create_horizontal_member_y(
        x,
        y_left,
        y_right,
        z_bottom,
        thickness,
        flange_width,
        section_type, 
        section_props, 
        roll_sign
    )
    braces.append(bottom_member)


    # Optional top bracket

    if top_bracket:
        top_member = create_horizontal_member_y(
            x,
            y_left,
            y_right,
            z_top,
            thickness,
            flange_width,
            section_type, 
            section_props, 
            roll_sign
        )
        braces.append(top_member)

    return braces
