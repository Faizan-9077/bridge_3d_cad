# deck.py
from OCC.Core.gp import gp_Trsf, gp_Vec
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Transform


def create_deck_slab(
    span_length,
    num_girders,
    girder_spacing,
    deck_overhang,
    deck_thickness,
    girder_depth
):
    """
    Creates and positions the deck slab above the girders.
    """

    total_width = (num_girders - 1) * girder_spacing + 2 * deck_overhang

    slab = BRepPrimAPI_MakeBox(
        span_length,
        total_width,
        deck_thickness
    ).Shape()

    trsf = gp_Trsf()
    trsf.SetTranslation(
        gp_Vec(
            0,
            -total_width / 2,
            girder_depth
        )
    )

    return BRepBuilderAPI_Transform(slab, trsf).Shape()
