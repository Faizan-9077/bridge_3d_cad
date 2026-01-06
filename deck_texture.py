# deck_texture.py
# Drafting-style concrete texture for deck
# - dots + random triangles
# - ONLY vertical faces: FRONT, BACK, LEFT, RIGHT
# - visual only (no structural meaning)

from OCC.Core.BRepPrimAPI import (
    BRepPrimAPI_MakeCylinder,
    BRepPrimAPI_MakePrism
)
from OCC.Core.BRepBuilderAPI import (
    BRepBuilderAPI_MakePolygon,
    BRepBuilderAPI_MakeFace,
    BRepBuilderAPI_Transform
)
from OCC.Core.gp import (
    gp_Pnt, gp_Trsf, gp_Vec,
    gp_Ax1, gp_Dir
)
import random
import math


# --------------------------------------------------
# GLOBAL SAFE MARGINS (IMPORTANT)
# --------------------------------------------------
DOT_RADIUS = 6
DOT_HEIGHT = 3

TRI_SIZE_MAX = 120
TRI_HEIGHT = 0.4

EDGE_GAP = 15     # minimum gap from any deck edge
Z_GAP = 15        # gap from top & bottom


# --------------------------------------------------
# Texture primitives
# --------------------------------------------------
def _create_dot(x, y, z, radius=DOT_RADIUS, height=DOT_HEIGHT):
    dot = BRepPrimAPI_MakeCylinder(radius, height).Shape()
    trsf = gp_Trsf()
    trsf.SetTranslation(gp_Vec(x, y, z))
    return BRepBuilderAPI_Transform(dot, trsf, True).Shape()


def _create_triangle(x, y, z, rot_axis=None, rot_angle=0):
    size = random.uniform(80, TRI_SIZE_MAX)

    # --- triangle points (local space) ---
    p1 = gp_Pnt(0, 0, 0)
    p2 = gp_Pnt(size, random.uniform(10, size), 0)
    p3 = gp_Pnt(random.uniform(10, size), size, 0)

    poly = BRepBuilderAPI_MakePolygon()
    poly.Add(p1)
    poly.Add(p2)
    poly.Add(p3)
    poly.Close()

    face = BRepBuilderAPI_MakeFace(poly.Wire()).Face()
    prism = BRepPrimAPI_MakePrism(face, gp_Vec(0, 0, TRI_HEIGHT)).Shape()

    # --------------------------------------------------
    # 1. CENTER the triangle about its own centroid
    # --------------------------------------------------
    center_trsf = gp_Trsf()
    center_trsf.SetTranslation(
        gp_Vec(-size / 2, -size / 2, -TRI_HEIGHT / 2)
    )
    prism = BRepBuilderAPI_Transform(prism, center_trsf, True).Shape()

    # --------------------------------------------------
    # 2. Apply rotation (if any)
    # --------------------------------------------------
    trsf = gp_Trsf()
    if rot_axis:
        trsf.SetRotation(rot_axis, rot_angle)

    trsf.SetTranslationPart(gp_Vec(x, y, z))

    return BRepBuilderAPI_Transform(prism, trsf, True).Shape()

# --------------------------------------------------
# Public API (4 vertical faces only)
# --------------------------------------------------
def generate_deck_texture(
    deck_length,
    deck_width,
    deck_thickness
):
    """
    Generates drafting-style texture ONLY on:
    - Front (Y+)
    - Back  (Y-)
    - Left  (X-)
    - Right (X+)
    """

    elements = []

    z_min = Z_GAP
    z_max = deck_thickness - Z_GAP - max(DOT_HEIGHT, TRI_HEIGHT)

    # --------------------------------------------------
    # FRONT & BACK FACES (Y)
    # --------------------------------------------------
    rot_y = gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(1, 0, 0))

    for y in (0.2, deck_width - 0.2):
        for _ in range(120):
            elements.append(
                _create_dot(
                    random.uniform(
                        EDGE_GAP,
                        deck_length - EDGE_GAP
                    ),
                    y,
                    random.uniform(z_min, z_max)
                )
            )

        for _ in range(15):
            elements.append(
                _create_triangle(
                    random.uniform(
                        EDGE_GAP,
                        deck_length - EDGE_GAP - TRI_SIZE_MAX
                    ),
                    y,
                    random.uniform(z_min, z_max),
                    rot_y,
                    math.pi / 2
                )
            )

    # --------------------------------------------------
    # LEFT & RIGHT FACES (X)
    # --------------------------------------------------
    rot_x = gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(0, 1, 0))

    for x in (0.2, deck_length - 0.2):
        for _ in range(100):
            elements.append(
                _create_dot(
                    x,
                    random.uniform(
                        EDGE_GAP,
                        deck_width - EDGE_GAP
                    ),
                    random.uniform(z_min, z_max)
                )
            )

        for _ in range(20):
            elements.append(
                _create_triangle(
                    x,
                    random.uniform(
                        EDGE_GAP,
                        deck_width - EDGE_GAP - TRI_SIZE_MAX
                    ),
                    random.uniform(z_min, z_max),
                    rot_x,
                    -math.pi / 2
                )
            )

    return elements


# --------------------------------------------------
# Centering helper
# --------------------------------------------------
def shift_texture_to_center(texture_shapes, deck_width):
    """
    Shifts texture from [0, deck_width] to [-deck_width/2, +deck_width/2]
    so it matches deck centered at Y = 0
    """
    trsf = gp_Trsf()
    trsf.SetTranslation(gp_Vec(0, -deck_width / 2, 0))

    return [
        BRepBuilderAPI_Transform(s, trsf, True).Shape()
        for s in texture_shapes
    ]


# --------------------------------------------------
# Placement helper
# --------------------------------------------------
def place_deck_texture(
    deck_length,
    deck_width,
    deck_thickness,
    deck_top_z
):
    """
    Generates, centers, and places texture on
    FRONT + BACK + LEFT + RIGHT faces of deck.
    """

    texture_shapes = generate_deck_texture(
        deck_length=deck_length,
        deck_width=deck_width,
        deck_thickness=deck_thickness
    )

    texture_shapes = shift_texture_to_center(
        texture_shapes,
        deck_width=deck_width
    )

    trsf = gp_Trsf()
    trsf.SetTranslation(
        gp_Vec(0, 0, deck_top_z - deck_thickness)
    )

    return [
        BRepBuilderAPI_Transform(s, trsf, True).Shape()
        for s in texture_shapes
    ]
