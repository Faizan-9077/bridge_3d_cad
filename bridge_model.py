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
deck_overhang = 1000   #extra slab beyond outer girders


#cross bracing parameters
cross_bracing_spacing = 6000 
cross_bracing_thickness = 80


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




# Assembles the bridge superstructure by combining all components
def assemble_bridge():
    girders = build_girders()
    cross_bracings = build_cross_bracing()
    deck = build_deck()
    return girders, cross_bracings, deck

# Main function: validates inputs, builds geometry, and displays the model
def main():
    validate_bridge_inputs(
    num_girders,
    girder_spacing,
    span_length_L,
    cross_bracing_spacing
    )


    display, start_display, _, _ = init_display()
    
    girders, cross_bracings, deck = assemble_bridge()

    for g in girders:
        display.DisplayShape(g, update=False)

    for cb in cross_bracings:
        display.DisplayShape(cb, update=False)

    display.DisplayShape(deck, update=False)

    display.View.SetProj(1, 0, 0)   # Front view
    display.FitAll()
    display.Repaint()

    start_display()



if __name__ == "__main__":
    main()
