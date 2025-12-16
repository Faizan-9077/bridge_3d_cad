# bridge_model.py
# Parametric 3D CAD Model of Steel Girder Bridge


from OCC.Display.backend import load_backend
load_backend("pyside6")

from OCC.Display.SimpleGui import init_display
from OCC.Core.gp import gp_Trsf, gp_Vec
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Transform

from deck import create_deck_slab
from draw_i_section import create_i_section
from cross_bracing import create_cross_bracing
from validation import validate_bridge_inputs
from railing import create_railing, place_railing
from crash_barriers import create_crash_barrier, place_crash_barrier



# NOTE:
# Parameters are kept as explicit variables for clarity.
# They can be refactored into a dictionary later.


# =====================
# PARAMETERS (mm)
# =====================

#girders parameters
span_length_L = 25000
girder_section_d = 900
girder_section_bf = 300
girder_section_tf = 160
girder_section_tw = 100
num_girders = 5           # number of main girders (>=3)
girder_spacing = 2750        # center-to-center spacing (mm)

#deck parameters
deck_thickness = 200
deck_overhang = 3000   #extra slab beyond outer girders

# carriageway & footpath (mm)
carriageway_width = 10500
footpath_width = 1120   # footpath on ONE side only


#cross bracing parameters
cross_bracing_spacing = 6000 
cross_bracing_thickness = 80

# crash barrier parameters (mm)
crash_barrier_base_width = 600
crash_barrier_top_width = 300
crash_barrier_height = 1100

# railing parameters (mm)
railing_width = 200
railing_height = 1200


#Function for multiple girders
def build_girders():
    girders = []

    total_width = (num_girders - 1) * girder_spacing

    for i in range(num_girders):
        # create base girder
        girder = create_i_section(
            span_length_L,
            girder_section_bf,
            girder_section_d,
            girder_section_tf,
            girder_section_tw
        )

        y_offset = (i * girder_spacing) - (total_width / 2)

        # translate girder along Y-axis
        trsf = gp_Trsf()
        trsf.SetTranslation(gp_Vec(0, y_offset, 0))

        moved_girder = BRepBuilderAPI_Transform(girder, trsf).Shape()
        girders.append(moved_girder)

    return girders


#Function for bulding deck
def build_deck():
    deck = create_deck_slab(
        span_length_L,
        num_girders,
        girder_spacing,
        deck_overhang,
        deck_thickness,
        girder_section_d
    )
    return deck

#Function for building cross-bracings
def build_cross_bracing():
    cross_bracings = create_cross_bracing(
        span_length_L,
        girder_spacing,
        num_girders,
        girder_section_d,
        girder_section_tf,
        cross_bracing_spacing,
        cross_bracing_thickness,
    )
    return cross_bracings

#Function for building crash_barriers
def build_crash_barrier(deck_top_z):
    """
    Builds crash barrier at deck edges (parametric)
    """

    crash_barriers = []

    base_barrier = create_crash_barrier(
        length=span_length_L,
        base_width=crash_barrier_base_width,
        top_width=crash_barrier_top_width,
        height=crash_barrier_height
)

    # ---- Deck geometry ----
    girder_outer_y = (num_girders - 1) * girder_spacing / 2
    deck_edge_y = girder_outer_y + deck_overhang

    barrier_offset = crash_barrier_base_width / 2
    barrier_y = deck_edge_y - barrier_offset

    # +Y side
    crash_barriers.append(
        place_crash_barrier(
            base_barrier,
            x=0,
            y=barrier_y,
            z=deck_top_z
        )
    )

    # -Y side
    crash_barriers.append(
        place_crash_barrier(
            base_barrier,
            x=0,
            y=-(girder_outer_y + girder_section_bf/2),
            z=deck_top_z
        )
    )

    return crash_barriers


#Function for building railing
def build_railing(deck_top_z):
    """
    Builds railing at extreme left edge of deck
    """
    railings = []

    base_railing = create_railing(
        length=span_length_L,
        width=railing_width,
        height=railing_height
    )

    # ---- Deck geometry ----
    girder_outer_y = (num_girders - 1) * girder_spacing / 2
    deck_edge_y = girder_outer_y + deck_overhang

    # extreme LEFT edge (negative Y)
    railing_y = -(deck_edge_y - railing_width / 2)

    railings.append(
        place_railing(
            base_railing,
            x=span_length_L / 2,
            y=railing_y,
            z=deck_top_z
        )
    )

    return railings




# Assembles the bridge superstructure by combining all components
def assemble_bridge():
    girders = build_girders()
    cross_bracings = build_cross_bracing()
    deck = build_deck()
    deck_top_z = girder_section_d + deck_thickness
    crash_barriers = build_crash_barrier(deck_top_z)
    railings = build_railing(deck_top_z)

    return girders, cross_bracings, deck, crash_barriers, railings

# Main function: validates inputs, builds geometry, and displays the model
def main():
    validate_bridge_inputs(
    num_girders,
    girder_spacing,
    span_length_L,
    cross_bracing_spacing
    )


    display, start_display, _, _ = init_display()
    
    girders, cross_bracings, deck, crash_barriers, railings = assemble_bridge()
    for g in girders:
        display.DisplayShape(g, update=False)

    for cb in cross_bracings:
        display.DisplayShape(cb, update=False)

    display.DisplayShape(deck, update=False)
    
    for cb in crash_barriers:
        display.DisplayShape(cb, update=False)

    for r in railings:
        display.DisplayShape(r, update=False)

    display.View.SetProj(1, 0, 0)   # Front view
    display.FitAll()
    display.Repaint()

    start_display()



if __name__ == "__main__":
    main()
