# cross_bracing.py
# X-type cross bracing for steel girder bridge
# Simple visual-stable implementation (length * 0.92)

from OCC.Core.gp import gp_Pnt, gp_Vec, gp_Trsf, gp_Ax1, gp_Dir
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Transform


# ------------------------------------------------------------
# Core function: diagonal bracing member
# ------------------------------------------------------------

def make_diagonal_member(p1, p2, thickness):
    """
    Creates a diagonal steel bracing member between two points.
    Length is NOT reduced.
    Member is shifted slightly along its direction for visual centering.
    """

    # Vector from p1 to p2
    vec = gp_Vec(p1, p2)
    length = vec.Magnitude()

    

    # 1. Create full-length box along X-axis
    box = BRepPrimAPI_MakeBox(
        length,
        thickness,
        thickness
    ).Shape()

    # 2. Rotate box to align with p1 -> p2
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

    # 3. Shift slightly along diagonal direction (visual fix)
    dir_vec = gp_Vec(vec.X(), vec.Y(), vec.Z())
    dir_vec.Normalize()
    dir_vec.Multiply(thickness)   # adjust if needed

    trsf_trans = gp_Trsf()
    trsf_trans.SetTranslation(
        gp_Vec(
            p1.X() + dir_vec.X(),
            p1.Y() + dir_vec.Y(),
            p1.Z() + dir_vec.Z()
        )
    )

    box = BRepBuilderAPI_Transform(box, trsf_trans).Shape()

    return box



def make_horizontal_member_y(x, y1, y2, z, thickness):
    """
    Creates a horizontal bracing member along Y-direction
    between y1 and y2 at given x and z.
    """

    length = abs(y2 - y1)

    box = BRepPrimAPI_MakeBox(
        thickness,   # X thickness
        length,      # Y length
        thickness    # Z thickness
    ).Shape()

    trsf = gp_Trsf()
    trsf.SetTranslation(
        gp_Vec(
            x - thickness / 2,
            min(y1, y2),
            z - thickness / 2
        )
    )

    box = BRepBuilderAPI_Transform(box, trsf).Shape()

    return box


# ------------------------------------------------------------
# X bracing between two adjacent girders
# ------------------------------------------------------------

def create_x_bracing_between_girders(
    x,
    y1,
    y2,
    girder_depth,
    flange_thickness,
    thickness
):
    """
    Creates X-type cross bracing between two adjacent girders.
    """

    braces = []

    # Web–flange junction levels
    z_bottom = flange_thickness
    z_top = girder_depth - flange_thickness

    # Diagonal /
    p1 = gp_Pnt(x, y1, z_bottom)
    p2 = gp_Pnt(x, y2, z_top)
    d1 = make_diagonal_member(p1, p2, thickness)

    # Diagonal \
    p3 = gp_Pnt(x, y1, z_top)
    p4 = gp_Pnt(x, y2, z_bottom)
    d2 = make_diagonal_member(p3, p4, thickness)

    # Bottom horizontal member
    bottom_member = make_horizontal_member_y(
        x,
        y1,
        y2,
        z_bottom,
        thickness
    )

    braces.append(bottom_member)

    # Top horizontal member
    top_member = make_horizontal_member_y(
        x,
        y1,
        y2,
        z_top,
        thickness
    )
    braces.append(top_member)


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
    flange_thickness,
    bracing_spacing,
    thickness
):
    """
    Builds X-type cross bracing along the bridge span.
    """

    cross_bracings = []

    total_width = (n_girders - 1) * girder_spacing
    n_braces = int(span_length / bracing_spacing) + 1

    for i in range(n_braces):
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
                    flange_thickness,
                    thickness
                )
            )

    return cross_bracings
