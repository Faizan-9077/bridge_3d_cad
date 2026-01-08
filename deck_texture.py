# deck_texture.py
# Drafting-style concrete texture for deck
# - dots + random triangles
# - ALL 6 faces: FRONT, BACK, LEFT, RIGHT, TOP, BOTTOM

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


DOT_RADIUS = 6
DOT_HEIGHT = 3

TRI_SIZE_MAX = 120
TRI_HEIGHT = 0.4

EDGE_GAP = 15
Z_GAP = 15


# Texture primitives
def _create_dot(x, y, z, radius=DOT_RADIUS, height=DOT_HEIGHT):
    dot = BRepPrimAPI_MakeCylinder(radius, height).Shape()
    trsf = gp_Trsf()
    trsf.SetTranslation(gp_Vec(x, y, z))
    return BRepBuilderAPI_Transform(dot, trsf, True).Shape()


def _create_dot_z(x, y, z, up=True):
    height = DOT_HEIGHT if up else -DOT_HEIGHT
    dot = BRepPrimAPI_MakeCylinder(DOT_RADIUS, abs(height)).Shape()
    trsf = gp_Trsf()
    trsf.SetTranslation(gp_Vec(x, y, z))
    return BRepBuilderAPI_Transform(dot, trsf, True).Shape()


def _create_triangle(x, y, z, rot_axis=None, rot_angle=0):
    size = random.uniform(80, TRI_SIZE_MAX)

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

    # center about its own centroid
    center_trsf = gp_Trsf()
    center_trsf.SetTranslation(
        gp_Vec(-size / 2, -size / 2, -TRI_HEIGHT / 2)
    )
    prism = BRepBuilderAPI_Transform(prism, center_trsf, True).Shape()

    trsf = gp_Trsf()
    if rot_axis:
        trsf.SetRotation(rot_axis, rot_angle)

    trsf.SetTranslationPart(gp_Vec(x, y, z))
    return BRepBuilderAPI_Transform(prism, trsf, True).Shape()


def _create_triangle_xy(x, y, z, up=True):
    size = random.uniform(80, TRI_SIZE_MAX)

    p1 = gp_Pnt(0, 0, 0)
    p2 = gp_Pnt(size, random.uniform(10, size), 0)
    p3 = gp_Pnt(random.uniform(10, size), size, 0)

    poly = BRepBuilderAPI_MakePolygon()
    poly.Add(p1)
    poly.Add(p2)
    poly.Add(p3)
    poly.Close()

    face = BRepBuilderAPI_MakeFace(poly.Wire()).Face()
    height = TRI_HEIGHT if up else -TRI_HEIGHT
    prism = BRepPrimAPI_MakePrism(face, gp_Vec(0, 0, height)).Shape()

    center_trsf = gp_Trsf()
    center_trsf.SetTranslation(gp_Vec(-size / 2, -size / 2, 0))
    prism = BRepBuilderAPI_Transform(prism, center_trsf, True).Shape()

    trsf = gp_Trsf()
    trsf.SetTranslation(gp_Vec(x, y, z))
    return BRepBuilderAPI_Transform(prism, trsf, True).Shape()


def generate_deck_texture(
    deck_length,
    deck_width,
    deck_thickness
):
    elements = []

    z_min = Z_GAP
    z_max = deck_thickness - Z_GAP - max(DOT_HEIGHT, TRI_HEIGHT)

    # FRONT & BACK (Y faces)
    rot_y = gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(1, 0, 0))

    for y in (0.2, deck_width - 0.2):
        for _ in range(120):
            elements.append(
                _create_dot(
                    random.uniform(EDGE_GAP, deck_length - EDGE_GAP),
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

    # LEFT & RIGHT (X faces)
    rot_x = gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(0, 1, 0))

    for x in (0.2, deck_length - 0.2):
        for _ in range(100):
            elements.append(
                _create_dot(
                    x,
                    random.uniform(EDGE_GAP, deck_width - EDGE_GAP),
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

    # TOP & BOTTOM (Z faces)
    for z, up in (
        (deck_thickness - 0.2, True),   # TOP
        (0.2, False)                   # BOTTOM
    ):
        for _ in range(150):
            elements.append(
                _create_dot_z(
                    random.uniform(EDGE_GAP, deck_length - EDGE_GAP),
                    random.uniform(EDGE_GAP, deck_width - EDGE_GAP),
                    z,
                    up=up
                )
            )

        for _ in range(50):
            elements.append(
                _create_triangle_xy(
                    random.uniform(
                        EDGE_GAP,
                        deck_length - EDGE_GAP - TRI_SIZE_MAX
                    ),
                    random.uniform(
                        EDGE_GAP,
                        deck_width - EDGE_GAP - TRI_SIZE_MAX
                    ),
                    z,
                    up=up
                )
            )

    return elements


# Centering helper
def shift_texture_to_center(texture_shapes, deck_width):
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
