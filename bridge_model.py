# bridge_model.py
# Parametric 3D CAD Model of Steel Girder Bridge
# Supports 3 footpath configurations: NONE, LEFT, RIGHT, BOTH

from OCC.Display.backend import load_backend
load_backend("pyside6")

from OCC.Display.SimpleGui import init_display
from OCC.Core.gp import gp_Trsf, gp_Vec
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCC.Core.Quantity import Quantity_Color, Quantity_TOC_RGB

from deck import create_deck_slab
from draw_i_section import create_i_section
from validation import validate_bridge_inputs
from railing import create_railing, place_railing
from cross_bracing import (
    create_x_bracing_between_girders,
    create_k_bracing_between_girders
)
from crash_barriers import place_crash_barrier, create_crash_barrier_left, create_crash_barrier_right

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

# footpath configuration
# Options: "NONE", "LEFT", "RIGHT", "BOTH"
footpath_config = "BOTH"
# footpath_width = 2000

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
crash_barrier_width = 175       # overall top width
crash_barrier_height = 900       # total height
crash_barrier_base_width = 450   # base width

# railing parameters (mm)
railing_width = 200
railing_height = 1200

# COLORS
COLOR_GIRDER        = (72/255, 72/255, 54/255)
COLOR_DECK          = (0.50, 0.50, 0.50)
COLOR_CROSS_BRACING = (134/255, 134/255, 100/255)
COLOR_CRASH_BARRIER = (83/255, 83/255, 83/255)
COLOR_RAILING       = (0.2, 0.2, 0.2)


def build_girders():
    """
    Builds girders symmetrically across the centerline.
    Girder positions are INDEPENDENT of footpath/crash barrier configuration.
    """
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

        # Symmetric placement from centerline
        y_offset = (i * girder_spacing) - (total_width / 2)

        trsf = gp_Trsf()
        trsf.SetTranslation(gp_Vec(0, y_offset, 0))

        moved_girder = BRepBuilderAPI_Transform(girder, trsf).Shape()
        girders.append(moved_girder)

    return girders


def build_deck():
    """Builds the deck slab"""
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
    """Builds cross bracing between girders"""
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
    Builds crash barriers based on footpath configuration.
    
    CASE 1 - NONE: Crash barriers at both deck edges
    CASE 2 - LEFT: Crash barrier at right edge + crash barrier before left footpath
    CASE 2 - RIGHT: Crash barrier at left edge + crash barrier before right footpath
    CASE 3 - BOTH: Crash barriers in middle (before both footpaths)
    """
    crash_barriers = []

    # Calculate key Y positions
    girder_outer_y = (num_girders - 1) * girder_spacing / 2
    deck_edge_y = girder_outer_y + deck_overhang
    
    
    # CASE 1: NO FOOTPATH
   
    if footpath_config == "NONE":
        # Right edge crash barrier (at +Y deck edge) - use RIGHT facing barrier
        barrier_right = create_crash_barrier_right(
            length=span_length_L,
            width=crash_barrier_width,
            height=crash_barrier_height,
            base_width=crash_barrier_base_width
        )
        barrier_y_right = deck_edge_y - crash_barrier_width / 2
        crash_barriers.append(
            place_crash_barrier(
                barrier_right,
                x=0,
                y=barrier_y_right,
                z=deck_top_z
            )
        )
        
        # Left edge crash barrier (at -Y deck edge) - use LEFT facing barrier
        barrier_left = create_crash_barrier_left(
            length=span_length_L,
            width=crash_barrier_width,
            height=crash_barrier_height,
            base_width=crash_barrier_base_width
        )
        barrier_y_left = -deck_edge_y + crash_barrier_width / 2
        crash_barriers.append(
            place_crash_barrier(
                barrier_left,
                x=0,
                y=barrier_y_left,
                z=deck_top_z
            )
        )
    
  
    # CASE 2: LEFT FOOTPATH ONLY

    elif footpath_config == "LEFT":
        # Right edge crash barrier (no footpath on this side) - use RIGHT facing barrier
        barrier_right = create_crash_barrier_right(
            length=span_length_L,
            width=crash_barrier_width,
            height=crash_barrier_height,
            base_width=crash_barrier_base_width
        )
        barrier_y_right = deck_edge_y - crash_barrier_width / 2 + girder_section_tw
        crash_barriers.append(
            place_crash_barrier(
                barrier_right,
                x=0,
                y=barrier_y_right,
                z=deck_top_z
            )
        )
        
        # Left side: crash barrier BEFORE footpath - use LEFT facing barrier
        barrier_left = create_crash_barrier_left(
            length=span_length_L,
            width=crash_barrier_width,
            height=crash_barrier_height,
            base_width=crash_barrier_base_width
        )
        barrier_y_left_middle = -(girder_outer_y + crash_barrier_width / 2)
        crash_barriers.append(
            place_crash_barrier(
                barrier_left,
                x=0,
                y=barrier_y_left_middle,
                z=deck_top_z
            )
        )
    
  
    # CASE 2: RIGHT FOOTPATH ONLY
  
    elif footpath_config == "RIGHT":
        # Left edge crash barrier (no footpath on this side) - use LEFT facing barrier
        barrier_left = create_crash_barrier_left(
            length=span_length_L,
            width=crash_barrier_width,
            height=crash_barrier_height,
            base_width=crash_barrier_base_width
        )
        barrier_y_left = -deck_edge_y + crash_barrier_width / 2 - girder_section_tw
        crash_barriers.append(
            place_crash_barrier(
                barrier_left,
                x=0,
                y=barrier_y_left,
                z=deck_top_z
            )
        )
        
        # Right side: crash barrier BEFORE footpath - use RIGHT facing barrier
        barrier_right = create_crash_barrier_right(
            length=span_length_L,
            width=crash_barrier_width,
            height=crash_barrier_height,
            base_width=crash_barrier_base_width
        )
        barrier_y_right_middle = girder_outer_y - crash_barrier_width / 2
        crash_barriers.append(
            place_crash_barrier(
                barrier_right,
                x=0,
                y=barrier_y_right_middle,
                z=deck_top_z
            )
        )
    
  
    # CASE 3: BOTH FOOTPATHS
    elif footpath_config == "BOTH":
        
        # Use crash_barrier_base_width (the wider bottom)
        offset = crash_barrier_base_width / 2
        
        # Right side: traffic faces inward (negative Y) - use RIGHT facing barrier
        barrier_right = create_crash_barrier_left(
            length=span_length_L,
            width=crash_barrier_width,
            height=crash_barrier_height,
            base_width=crash_barrier_base_width
        )
        barrier_y_right = girder_outer_y + offset
        crash_barriers.append(
            place_crash_barrier(
                barrier_right,
                x=0,
                y=barrier_y_right,
                z=deck_top_z
            )
        )

        # Left side: traffic faces inward (positive Y) - use LEFT facing barrier
        barrier_left = create_crash_barrier_right(
            length=span_length_L,
            width=crash_barrier_width,
            height=crash_barrier_height,
            base_width=crash_barrier_base_width
        )
        barrier_y_left = -(girder_outer_y + offset)
        crash_barriers.append(
            place_crash_barrier(
                barrier_left,
                x=0,
                y=barrier_y_left,
                z=deck_top_z
            )
        )

        print("Right Y:", barrier_y_right)
        print("Left  Y:", barrier_y_left)

        print(f"crash_barrier_width = {crash_barrier_width}")
        print(f"crash_barrier_base_width = {crash_barrier_base_width}")
        print(f"girder_section_bf = {girder_section_bf}")
        print(f"Barrier extends ±{crash_barrier_base_width/2} from its center")

    return crash_barriers


def build_railing(deck_top_z):
    """
    Builds railings based on footpath configuration.
    
    CASE 1 - NONE: No railings
    CASE 2 - LEFT: Railing at left deck edge
    CASE 2 - RIGHT: Railing at right deck edge
    CASE 3 - BOTH: Railings at both deck edges
    """
    railings = []

    # No railings for NONE case
    if footpath_config == "NONE":
        return railings

    # Create base railing shape
    base_railing = create_railing(
        length=span_length_L,
        width=railing_width,
        height=railing_height
    )

    # Calculate deck edge position
    girder_outer_y = (num_girders - 1) * girder_spacing / 2
    deck_edge_y = girder_outer_y + deck_overhang

    # ========================================
    # LEFT FOOTPATH - Railing at left edge
    # ========================================
    if footpath_config == "LEFT" or footpath_config == "BOTH":
        railing_y_left = -(deck_edge_y - railing_width / 2)
        railings.append(
            place_railing(
                base_railing,
                x=span_length_L / 2,
                y=railing_y_left,
                z=deck_top_z
            )
        )

    # ========================================
    # RIGHT FOOTPATH - Railing at right edge
    # ========================================
    if footpath_config == "RIGHT" or footpath_config == "BOTH":
        railing_y_right = deck_edge_y - railing_width / 2
        railings.append(
            place_railing(
                base_railing,
                x=span_length_L / 2,
                y=railing_y_right,
                z=deck_top_z
            )
        )

    return railings


def display_colored(display, shape, rgb):
    """Helper function to display shapes with color"""
    display.DisplayShape(
        shape,
        color=Quantity_Color(*rgb, Quantity_TOC_RGB),
        update=False
    )


def assemble_bridge():
    """Assembles all bridge components"""
    girders = build_girders()
    cross_bracings = build_cross_bracing()
    deck = build_deck()
    deck_top_z = girder_section_d + deck_thickness
    crash_barriers = build_crash_barrier(deck_top_z)
    railings = build_railing(deck_top_z)

    return girders, cross_bracings, deck, crash_barriers, railings


def main():
    """Main function to build and display the bridge"""
    
    # Validate inputs
    validate_bridge_inputs(
        num_girders,
        girder_spacing,
        span_length_L,
        cross_bracing_spacing,
        deck_thickness=deck_thickness,
        footpath_config=footpath_config,
        # footpath_width=footpath_width
    )


    # Print configuration for user reference
    print("=" * 60)
    print("BRIDGE CONFIGURATION")
    print("=" * 60)
    print(f"Footpath Configuration: {footpath_config}")
    print(f"Number of Girders: {num_girders}")
    print(f"Girder Spacing: {girder_spacing} mm")
    print(f"Deck Overhang: {deck_overhang} mm")
    print(f"Total Deck Width: {total_deck_width} mm")
    print(f"Carriageway Width: {carriageway_width} mm")

    # Initialize display
    display, start_display, add_menu, add_function_to_menu = init_display()
    
    # Assemble bridge components
    girders, cross_bracings, deck, crash_barriers, railings = assemble_bridge()
    
    # Display girders
    for g in girders:
        display_colored(display, g, COLOR_GIRDER)

    # Display cross bracings
    for cb in cross_bracings:
        display_colored(display, cb, COLOR_CROSS_BRACING)

    # Display deck
    display_colored(display, deck, COLOR_DECK)

    # Display crash barriers
    for cb in crash_barriers:
        display_colored(display, cb, COLOR_CRASH_BARRIER)

    # Display railings
    for r in railings:
        display_colored(display, r, COLOR_RAILING)

    # Set up arrow key panning
    from PySide6.QtCore import Qt

    def pan_up():
        display.Pan(0, 50)
    
    def pan_down():
        display.Pan(0, -50)
    
    def pan_left():
        display.Pan(-50, 0)
    
    def pan_right():
        display.Pan(50, 0)

    key_function = {
        Qt.Key.Key_Up: pan_up,
        Qt.Key.Key_Down: pan_down,
        Qt.Key.Key_Right: pan_right,
        Qt.Key.Key_Left: pan_left
    }
    
    try:
        if hasattr(display, '_inited_display'):
            canvas = display._inited_display
            if hasattr(canvas, '_key_map'):
                canvas._key_map.update(key_function)
        elif hasattr(display, 'parent'):
            if hasattr(display.parent, '_key_map'):
                display.parent._key_map.update(key_function)
    except AttributeError:
        print("Warning: Could not bind arrow keys for panning")

    # Set view and display
    display.View.SetProj(1, 0, 0)
    display.FitAll()
    display.Repaint()

    start_display()


if __name__ == "__main__":
    main()