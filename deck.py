# deck.py

from OCC.Core.gp import gp_Trsf, gp_Vec
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Transform

from draw_rectangular_prism import create_rectangular_prism


def create_deck_slab(
    span_length,
    deck_width,
    deck_thickness,
    girder_depth
):
    """
    Creates and positions the deck slab above the girders.
    Deck is centered at Y=0.
    
    Parameters:
    -----------
    span_length : float
        Length of the bridge span
    deck_width : float
        Total width of the deck (calculated based on footpath configuration)
    deck_thickness : float
        Thickness of the deck slab
    girder_depth : float
        Depth of the girder (to position deck on top)
    
    Returns:
    --------
    Positioned deck slab shape
    """

    # Create rectangular prism for deck
    slab = create_rectangular_prism(
        span_length,
        deck_width,
        deck_thickness
    )

    # Position deck: centered at Y=0, sitting on top of girders
    trsf = gp_Trsf()
    trsf.SetTranslation(
        gp_Vec(
            span_length / 2,
            0,  # Deck centered at Y=0
            girder_depth
        )
    )

    return BRepBuilderAPI_Transform(slab, trsf).Shape()