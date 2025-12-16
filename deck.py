# deck.py

from OCC.Core.gp import gp_Trsf, gp_Vec
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Transform

from draw_rectangular_prism import create_rectangular_prism


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

    # Use existing rectangular prism factory
    slab = create_rectangular_prism(
        span_length,
        total_width,
        deck_thickness
    )

    trsf = gp_Trsf()
    trsf.SetTranslation(
        gp_Vec(
            span_length/2,
            0,
            girder_depth
        )
    )

    return BRepBuilderAPI_Transform(slab, trsf).Shape()
