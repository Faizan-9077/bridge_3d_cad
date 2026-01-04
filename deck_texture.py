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


# Texture primitives
def _create_dot(x, y, z, radius=6, height=3):
    dot = BRepPrimAPI_MakeCylinder(radius, height).Shape()
    trsf = gp_Trsf()
    trsf.SetTranslation(gp_Vec(x, y, z))
    return BRepBuilderAPI_Transform(dot, trsf, True).Shape()


def _create_triangle(x, y, z, rot_axis=None, rot_angle=0):
    size = random.uniform(100, 120)

    p1 = gp_Pnt(0, 0, 0)
    p2 = gp_Pnt(size, random.uniform(10, size), 0)
    p3 = gp_Pnt(random.uniform(10, size), size, 0)

    poly = BRepBuilderAPI_MakePolygon()
    poly.Add(p1)
    poly.Add(p2)
    poly.Add(p3)
    poly.Close()

    face = BRepBuilderAPI_MakeFace(poly.Wire()).Face()
    prism = BRepPrimAPI_MakePrism(face, gp_Vec(0, 0, 0.4)).Shape()

    trsf = gp_Trsf()
    if rot_axis:
        trsf.SetRotation(rot_axis, rot_angle)

    trsf.SetTranslationPart(gp_Vec(x, y, z))
    return BRepBuilderAPI_Transform(prism, trsf, True).Shape()


# Public API (4 vertical faces only)
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

    # FRONT & BACK FACES (Y)
    rot_y = gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(1, 0, 0))

    for y in (0.2, deck_width - 0.2):  # back, front
        for _ in range(120):
            elements.append(
                _create_dot(
                    random.uniform(50, deck_length - 50),
                    y,
                    random.uniform(20, deck_thickness - 20)
                )
            )

        for _ in range(15):
            elements.append(
                _create_triangle(
                    random.uniform(50, deck_length - 80),
                    y,
                    random.uniform(20, deck_thickness - 20),
                    rot_y,
                    math.pi / 2
                )
            )

    # LEFT & RIGHT FACES (X)
    rot_x = gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(0, 1, 0))

    for x in (0.2, deck_length - 0.2):  # left, right
        for _ in range(100):
            elements.append(
                _create_dot(
                    x,
                    random.uniform(50, deck_width - 50),
                    random.uniform(20, deck_thickness - 20)
                )
            )

        for _ in range(20):
            elements.append(
                _create_triangle(
                    x,
                    random.uniform(50, deck_width - 80),
                    random.uniform(20, deck_thickness - 20),
                    rot_x,
                    -math.pi / 2
                )
            )

    return elements


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


# Placement helper
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

    # 1. Generate texture geometry
    texture_shapes = generate_deck_texture(
        deck_length=deck_length,
        deck_width=deck_width,
        deck_thickness=deck_thickness
    )

    # 2. Center in Y
    texture_shapes = shift_texture_to_center(
        texture_shapes,
        deck_width=deck_width
    )

    # 3. Lift to deck position
    trsf = gp_Trsf()
    trsf.SetTranslation(gp_Vec(0, 0, deck_top_z - deck_thickness))

    return [
        BRepBuilderAPI_Transform(s, trsf, True).Shape()
        for s in texture_shapes
    ]
