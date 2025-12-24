# bridge_model.py
# Parametric 3D CAD Model of Steel Girder Bridge

from OCC.Display.backend import load_backend
load_backend("pyside6")

from OCC.Display.SimpleGui import init_display
from OCC.Core.gp import gp_Trsf, gp_Vec
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Transform

from deck import create_deck_slab
from draw_i_section import create_i_section
from validation import validate_bridge_inputs
from railing import create_railing, place_railing
from cross_bracing import (
    create_x_bracing_between_girders,
    create_k_bracing_between_girders
)
from crash_barriers import place_crash_barrier, create_crash_barrier

# =====================
# PARAMETERS (mm)
# =====================

# girders parameters
span_length_L = 25000
girder_section_d = 900
girder_section_bf = 500
girder_section_tf = 260
girder_section_tw = 100
num_girders = 8
girder_spacing = 2750

# deck parameters
deck_thickness = 400
deck_overhang = 3000

# footpath 
footpath_width = 2000

# Derived widths
total_deck_width = (num_girders - 1) * girder_spacing + 2 * deck_overhang
carriageway_width = (num_girders - 1) * girder_spacing

# cross bracing parameters
cross_bracing_spacing = 4000 
cross_bracing_thickness = 100
bracing_type = "K"
# X bracing option: "NONE" | "LOWER" | "UPPER" | "BOTH"
x_bracket_option = "BOTH"

# K bracing option: top bracket optional
k_top_bracket = False

# crash barrier parameters (mm)
crash_barrier_base_width = 500
crash_barrier_toe_height = 200
crash_barrier_slope_height = 300
crash_barrier_top_vertical_height = 600
crash_barrier_mid_width_ratio = 0.75
crash_barrier_top_width = 250

# railing parameters (mm)
railing_width = 200
railing_height = 1200


def build_girders():
    girders = []
    total_width = (num_girders - 1) * girder_spacing

    for i in range(num_girders):
        girder = create_i_section(
            span_length_L,
            girder_section_bf,
            girder_section_d,
            girder_section_tf,
            girder_section_tw
        )

        y_offset = (i * girder_spacing) - (total_width / 2)

        trsf = gp_Trsf()
        trsf.SetTranslation(gp_Vec(0, y_offset, 0))

        moved_girder = BRepBuilderAPI_Transform(girder, trsf).Shape()
        girders.append(moved_girder)

    return girders


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
    cross_bracings = []

    # Number of bracing frames along span
    n = int(span_length_L / cross_bracing_spacing) - 1
    n_total = n + 2
    spacing = span_length_L / (n_total - 1)
    x_positions = [i * spacing for i in range(n_total)]

    total_width = (num_girders - 1) * girder_spacing

    for x in x_positions:
        for g in range(num_girders - 1):

            y_left = (g * girder_spacing) - total_width / 2
            y_right = ((g + 1) * girder_spacing) - total_width / 2

            if bracing_type == "X":
                cross_bracings.extend(
                    create_x_bracing_between_girders(
                        x=x,
                        y_left=y_left,
                        y_right=y_right,
                        girder_depth=girder_section_d,
                        flange_thickness=girder_section_tf,
                        thickness=cross_bracing_thickness,
                        flange_width=girder_section_bf,
                        bracket_option=x_bracket_option
                    )
                )

            elif bracing_type == "K":
                cross_bracings.extend(
                    create_k_bracing_between_girders(
                        x=x,
                        y_left=y_left,
                        y_right=y_right,
                        girder_depth=girder_section_d,
                        flange_thickness=girder_section_tf,
                        thickness=cross_bracing_thickness,
                        flange_width=girder_section_bf,
                        top_bracket=k_top_bracket
                    )
                )

            else:
                raise ValueError(
                    f"Invalid bracing_type '{bracing_type}'. "
                    "Allowed values are 'X' or 'K'."
                )

    return cross_bracings

def build_crash_barrier(deck_top_z):
    """
    Builds crash barrier at deck edges (parametric New Jersey type)
    Left barrier: rightmost edge at center of leftmost girder
    Right barrier: leftmost edge (traffic face) at center of rightmost girder
    Distance between barriers = carriageway_width
    """
    crash_barriers = []

    # Create base barrier with parametric shape control
    base_barrier = create_crash_barrier(
        span_length_L,
        crash_barrier_base_width,
        crash_barrier_toe_height,
        crash_barrier_slope_height,
        crash_barrier_top_vertical_height,
        crash_barrier_mid_width_ratio,
        crash_barrier_top_width
    )


    # Right barrier (+Y side)
    # Traffic face (Y=0) at center of rightmost girder
    barrier_y_right = carriageway_width / 2 + 1.5*girder_section_bf

    # Left barrier (-Y side)
    # Rightmost edge (Y=base_width) at center of leftmost girder
    barrier_y_left = -carriageway_width / 2 - girder_section_bf/2

    # Right side barrier
    crash_barriers.append(
        place_crash_barrier(
            base_barrier,
            x=0,
            y=barrier_y_right,
            z=deck_top_z,
            mirror=True
        )
    )

    # Left side barrier
    crash_barriers.append(
        place_crash_barrier(
            base_barrier,
            x=0,
            y=barrier_y_left,
            z=deck_top_z,
            mirror=False
        )
    )

    return crash_barriers


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

    # Deck geometry
    girder_outer_y = (num_girders - 1) * girder_spacing / 2
    deck_edge_y = girder_outer_y + deck_overhang

    # Extreme LEFT edge (negative Y)
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


def assemble_bridge():
    girders = build_girders()
    cross_bracings = build_cross_bracing()
    deck = build_deck()
    deck_top_z = girder_section_d + deck_thickness
    crash_barriers = build_crash_barrier(deck_top_z)
    railings = build_railing(deck_top_z)

    return girders, cross_bracings, deck, crash_barriers, railings


def main():
    validate_bridge_inputs(
        num_girders,
        girder_spacing,
        span_length_L,
        cross_bracing_spacing
    )

    display, start_display, add_menu, add_function_to_menu = init_display()
    
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

    from PySide6.QtCore import Qt

    # Pan/Rotate functions with proper closure over display object
    def pan_up():
        display.Pan(0, 50)
    
    def pan_down():
        display.Pan(0, -50)
    
    def pan_left():
        display.Pan(-50, 0)
    
    def pan_right():
        display.Pan(50, 0)

    # Map arrow keys to pan functions
    key_function = {
        Qt.Key.Key_Up: pan_up,
        Qt.Key.Key_Down: pan_down,
        Qt.Key.Key_Right: pan_right,
        Qt.Key.Key_Left: pan_left
    }
    
    # Access the canvas widget from the display's internal structure
    try:
        # Try to get the canvas/widget that handles keyboard input
        if hasattr(display, '_inited_display'):
            canvas = display._inited_display
            if hasattr(canvas, '_key_map'):
                canvas._key_map.update(key_function)
        # Alternative: try the parent window
        elif hasattr(display, 'parent'):
            if hasattr(display.parent, '_key_map'):
                display.parent._key_map.update(key_function)
    except AttributeError:
        print("Warning: Could not bind arrow keys for panning")

    display.View.SetProj(1, 0, 0)
    display.FitAll()
    display.Repaint()

    start_display()


if __name__ == "__main__":
    main()