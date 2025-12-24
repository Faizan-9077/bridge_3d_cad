# cross_bracing.py
# X-type cross bracing for steel girder bridge
# Fixed: Proper alignment when girders are centered around y=0

from OCC.Core.gp import gp_Pnt, gp_Vec, gp_Trsf, gp_Ax1, gp_Dir
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Transform


# ------------------------------------------------------------
# Core function: diagonal bracing member
# ------------------------------------------------------------

def make_diagonal_member(p1, p2, thickness):
    """
    Creates a diagonal steel bracing member between two points.
    Correctly aligned with no inward offset.
    """

    # Vector from p1 to p2
    vec = gp_Vec(p1, p2)
    length = vec.Magnitude()

    # 1. Create CENTERED box 
    box = BRepPrimAPI_MakeBox(
        length,
        thickness,
        thickness
    ).Shape()

    trsf_center = gp_Trsf()
    trsf_center.SetTranslation(
        gp_Vec(-length / 2, -thickness / 2, -thickness / 2)
    )
    box = BRepBuilderAPI_Transform(box, trsf_center).Shape()

    # 2. Rotate to match p1 → p2
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

    # 3. Translate EXACTLY to midpoint (p1 + p2)/2
    mid = gp_Pnt(
        (p1.X() + p2.X()) / 2,
        (p1.Y() + p2.Y()) / 2,
        (p1.Z() + p2.Z()) / 2
    )

    trsf_trans = gp_Trsf()
    trsf_trans.SetTranslation(
        gp_Vec(mid.X(), mid.Y(), mid.Z())
    )

    box = BRepBuilderAPI_Transform(box, trsf_trans).Shape()

    return box


def make_horizontal_member_y(y_left_girder_left_edge, y_right_girder_left_edge, x, z, thickness, flange_width):
    """
    Creates a horizontal bracing member along Y-direction.
    Member spans EXACTLY from the right edge of left flange to left edge of right flange.
    
    IMPORTANT: y_left_girder_left_edge and y_right_girder_left_edge are the LEFT edges
    of the flanges (where flange starts), NOT the centers!
    
    Args:
        y_left_girder_left_edge: Y-coordinate of LEFT girder's LEFT flange edge
        y_right_girder_left_edge: Y-coordinate of RIGHT girder's LEFT flange edge
        x, z: Position coordinates
        thickness: Thickness of the bracing member
        flange_width: Width (breadth) of the girder flange (bf)
    """

    # Calculate exact endpoints at flange edges
    # Since we receive LEFT edges, add flange_width to get RIGHT edge of left girder
    y_start = y_left_girder_left_edge + flange_width   # Right edge of left girder flange
    y_end = y_right_girder_left_edge                    # Left edge of right girder flange
    
    # Length is the distance between these two points
    length = y_end - y_start
    
    # Midpoint between the two webs
    y_mid = (y_start + y_end) / 2

    # Create box with exact length
    box = BRepPrimAPI_MakeBox(
        thickness,   # X thickness
        length,      # Y length (exact web-to-web distance)
        thickness    # Z thickness
    ).Shape()

    # Center it first
    trsf_center = gp_Trsf()
    trsf_center.SetTranslation(
        gp_Vec(-thickness / 2, -length / 2, -thickness / 2)
    )
    box = BRepBuilderAPI_Transform(box, trsf_center).Shape()

    # Then translate to final position (centered between webs)
    trsf = gp_Trsf()
    trsf.SetTranslation(
        gp_Vec(x, y_mid, z)
    )

    box = BRepBuilderAPI_Transform(box, trsf).Shape()

    return box






# ------------------------------------------------------------
# X bracing between two adjacent girders
# ------------------------------------------------------------

# ------------------------------------------------------------
# X bracing between two adjacent girders
# ------------------------------------------------------------

def create_x_bracing_between_girders(
    x,
    y_left,
    y_right,
    girder_depth,
    flange_thickness,
    thickness,
    flange_width
):
    
    """
    Creates X-type cross bracing between two adjacent girders.
    Diagonals connect at the web (flange-web junction).
    Horizontal chords span from flange edge to flange edge.
    
    Args:
        x: X-position along bridge span
        y_left: Y-coordinate of LEFT girder's LEFT edge (where flange starts)
        y_right: Y-coordinate of RIGHT girder's LEFT edge (where flange starts)
        girder_depth: Total depth of girder
        flange_thickness: Thickness of flanges
        thickness: Thickness of bracing members
        flange_width: Width (breadth) of girder flange
    """

    braces = []

    # Web–flange junction levels (where web starts/ends)
    z_bottom = flange_thickness/2
    z_top = girder_depth - flange_thickness/2

    y_left_diagonal = y_left + flange_width 
    y_right_diagonal = y_right

    # Diagonal / - connects from left-bottom to right-top (at web edges)
    p1 = gp_Pnt(x, y_left_diagonal, z_bottom)
    p2 = gp_Pnt(x, y_right_diagonal, z_top)
    d1 = make_diagonal_member(p1, p2, thickness)

    # Diagonal \ - connects from left-top to right-bottom (at web edges)
    p3 = gp_Pnt(x, y_left_diagonal, z_top)
    p4 = gp_Pnt(x, y_right_diagonal, z_bottom)
    d2 = make_diagonal_member(p3, p4, thickness)


    # Bottom horizontal chord - spans from flange edge to flange edge
    bottom_member = make_horizontal_member_y(
        y_left,
        y_right,
        x,
        z_bottom,
        thickness,
        flange_width
    )
    braces.append(bottom_member)

    # Top horizontal chord - spans from flange edge to flange edge
    top_member = make_horizontal_member_y(
        y_left,
        y_right,
        x,
        z_top,
        thickness,
        flange_width
    )
    braces.append(top_member)

    braces.append(d1)
    braces.append(d2)

    return braces


# ------------------------------------------------------------
# K bracing between two adjacent girders
# ------------------------------------------------------------

def create_k_bracing_between_girders(
    x,
    y_left,
    y_right,
    girder_depth,
    flange_thickness,
    thickness,
    flange_width
):
    
    """
    Creates K-type cross bracing between two adjacent girders.
    Diagonals connect from left/right girder webs to the midpoint of bottom chord.
    Horizontal chords span from flange edge to flange edge.
    
    Args:
        x: X-position along bridge span
        y_left: Y-coordinate of LEFT girder's LEFT edge (where flange starts)
        y_right: Y-coordinate of RIGHT girder's LEFT edge (where flange starts)
        girder_depth: Total depth of girder
        flange_thickness: Thickness of flanges
        thickness: Thickness of bracing members
        flange_width: Width (breadth) of girder flange
    """

    braces = []

    # Web–flange junction levels (where web starts/ends)
    z_bottom = flange_thickness/2
    z_top = girder_depth - flange_thickness/2

    # Web positions (right edge of left girder, left edge of right girder)
    y_left_diagonal = y_left + flange_width 
    y_right_diagonal = y_right
    
    # Midpoint of bottom chord (horizontally)
    y_mid = (y_left_diagonal + y_right_diagonal) / 2

    # Left diagonal - connects from left girder top to midpoint of bottom chord
    p1 = gp_Pnt(x, y_left_diagonal, z_top)
    p2 = gp_Pnt(x, y_mid, z_bottom)
    d1 = make_diagonal_member(p1, p2, thickness)

    # Right diagonal - connects from right girder top to midpoint of bottom chord
    p3 = gp_Pnt(x, y_right_diagonal, z_top)
    p4 = gp_Pnt(x, y_mid, z_bottom)
    d2 = make_diagonal_member(p3, p4, thickness)

    # Bottom horizontal chord - spans from flange edge to flange edge
    bottom_member = make_horizontal_member_y(
        y_left,
        y_right,
        x,
        z_bottom,
        thickness,
        flange_width
    )
    braces.append(bottom_member)

    # Top horizontal chord - spans from flange edge to flange edge
    top_member = make_horizontal_member_y(
        y_left,
        y_right,
        x,
        z_top,
        thickness,
        flange_width
    )
    braces.append(top_member)

    braces.append(d1)
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
    thickness,
    flange_width,
    bracing_type
):
    """
    Builds X-type cross bracing along the bridge span.
    Always places bracing at x=0 and x=span_length,
    with remaining bracing equally distributed based on bracing_spacing.
    
    IMPORTANT: This matches the girder positioning in build_girders():
    y_offset = (i * girder_spacing) - (total_width / 2)
    where y_offset is the LEFT edge of the flange (where I-section starts at y=0)
    
    Args:
        flange_width: Width (breadth) of girder flange (e.g., girder_section_bf)
    """

    cross_bracings = []
    
    # Calculate number of intermediate braces
    n_intermediate = int(span_length / bracing_spacing) - 1
    
    # Total number of braces including start and end
    n_total = n_intermediate + 2
    
    # Calculate equal spacing
    actual_spacing = span_length / (n_total - 1)
    
    # Build list of x positions with equal spacing
    x_positions = []
    for i in range(n_total):
        x_positions.append(i * actual_spacing)
    
    # Match the exact girder positioning formula from build_girders()
    total_width = (n_girders - 1) * girder_spacing

    for x in x_positions:
        # Loop through adjacent pairs of girders
        for g in range(n_girders - 1):
            # Calculate Y positions for LEFT edges of flanges (matching build_girders)
            y_left = (g * girder_spacing) - (total_width / 2)
            y_right = ((g + 1) * girder_spacing) - (total_width / 2)

            if bracing_type.upper() == "X":
                cross_bracings.extend(
                    create_x_bracing_between_girders(
                        x, 
                        y_left,      # Left girder's LEFT flange edge
                        y_right,     # Right girder's LEFT flange edge
                        girder_depth,
                        flange_thickness,
                        thickness,
                        flange_width
                    )
                )

            elif bracing_type.upper() == "K":
                cross_bracings.extend(
                    create_k_bracing_between_girders(
                        x,
                        y_left,
                        y_right,
                        girder_depth,
                        flange_thickness,
                        thickness,
                        flange_width
                    )
                )

            else:
                raise ValueError(
                    f"Unsupported bracing type: {bracing_type}. Use 'X' or 'K'."
                )
                

    return cross_bracings