
# bridge_model.py
# Parametric 3D CAD Model of Steel Girder Bridge


from OCC.Display.backend import load_backend
load_backend("pyside6")

from OCC.Display.SimpleGui import init_display
from OCC.Core.gp import gp_Trsf, gp_Vec
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCC.Core.Quantity import Quantity_Color, Quantity_TOC_RGB
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Fuse


from deck import create_deck_slab
from deck_texture import generate_deck_texture
from deck_texture import shift_texture_to_center
from deck_texture import place_deck_texture
from draw_i_section import create_i_section
from validation import validate_bridge_inputs
from railing import create_railing, place_railing
from cross_bracing import (
    create_x_bracing_between_girders,
    create_k_bracing_between_girders
)
from crash_barriers import place_crash_barrier, create_crash_barrier_left, create_crash_barrier_right
from sections.section_database import ISA_SECTIONS
from sections.section_database import get_section_props
from sections.stiffener_plate import create_girder_stiffeners



# =====================
# PARAMETERS (mm)
# =====================

# girders parameters
span_length_L = 25000
girder_section_d = 900
girder_section_bf = 500
girder_section_tf = 260
girder_section_tw = 100
num_girders = 5
girder_spacing = 2750

carriageway_width = 12000

# deck parameters
deck_thickness = 400

# footpath configuration
# Options: "NONE", "LEFT", "RIGHT", "BOTH"
footpath_config = "BOTH"
footpath_width = 2000

# cross bracing parameters
cross_bracing_spacing = 4000 
cross_bracing_thickness = 100
bracing_type = "X"
# X bracing option: "NONE" | "LOWER" | "UPPER" | "BOTH"
x_bracket_option = "BOTH"

# K bracing option: top bracket optional
k_top_bracket = True


cross_bracing_section_type = "DOUBLE_ANGLE"
cross_bracing_section_name = "ISA_90x60x6"

# Only used if section type is DOUBLE_ANGLE
cross_bracing_connection = "LONGER_LEG"

cross_bracing_section_props = get_section_props(
    cross_bracing_section_type,
    cross_bracing_section_name
)
if cross_bracing_section_type == "DOUBLE_ANGLE":
    cross_bracing_section_props = dict(cross_bracing_section_props)
    cross_bracing_section_props["connection_type"] = cross_bracing_connection




# crash barrier parameters (mm)
crash_barrier_width = 175       # overall top width
crash_barrier_height = 900       # total height
crash_barrier_base_width = 450   # base width

# railing parameters (mm)
railing_width = 375
railing_height = 1100
rail_count = 3

# STIFFENER PARAMETERS 
stiffener_width     = 200      
stiffener_length    = 300     



# COLORS
COLOR_GIRDER        = (72/255, 72/255, 54/255)
COLOR_DECK          = (0.7, 0.7, 0.7)
texture_color =  Quantity_Color(0.30, 0.30, 0.30, Quantity_TOC_RGB)
COLOR_CROSS_BRACING =  (95/255, 85/255, 110/255)      #(134/255, 134/255, 100/255)
COLOR_CRASH_BARRIER = (83/255, 83/255, 83/255)
COLOR_RAILING       = (0.2, 0.2, 0.2)
COLOR_STIFFENER = (30/255, 30/255, 30/255)




def build_girders():
    """
    Builds girders symmetrically across the centerline.
    """
    girders = []
    stiffeners = []
    total_width = (num_girders - 1) * girder_spacing

    for i in range(num_girders):

        # 1. Create I-girder 
        girder = create_i_section(
            span_length_L,
            girder_section_bf,
            girder_section_d,
            girder_section_tf,
            girder_section_tw
        )

       
        
        left_stiff, right_stiff = create_girder_stiffeners(
            girder_depth=girder_section_d,
            girder_flange_width=girder_section_bf,
            girder_web_thickness=girder_section_tw,
            girder_flange_thickness=girder_section_tf,
            stiffener_width=stiffener_width,
            stiffener_length=stiffener_length,
            x_offset=+span_length_L-stiffener_length
        )

        stiffeners.extend([left_stiff, right_stiff])

        # 3. Move girder to correct Y position
        y_offset = (i * girder_spacing) - (total_width / 2)

        trsf = gp_Trsf()
        trsf.SetTranslation(gp_Vec(0, y_offset, 0))

        moved_girder = BRepBuilderAPI_Transform(girder, trsf).Shape()
        girders.append(moved_girder)

        # Move stiffeners WITH girder
        stiffeners[-2] = BRepBuilderAPI_Transform(left_stiff, trsf).Shape()
        stiffeners[-1] = BRepBuilderAPI_Transform(right_stiff, trsf).Shape()

    return girders, stiffeners



def calculate_deck_width(footpath_config):
    """
    Calculates total deck width based on footpath configuration.
    
    Layout from center outward:
    - Carriageway (centered at Y=0)
    - Crash barriers (at carriageway edges)
    - Footpaths (if present)
    - Railings (at deck edges, if footpaths present)
    
    Returns:
    --------
    total_deck_width : float
    """
    
    if footpath_config == "NONE":
        # carriageway + 2 × crash_barrier_base_width
        return carriageway_width + 2 * crash_barrier_base_width
    
    elif footpath_config == "LEFT" or footpath_config == "RIGHT":
        # carriageway + 2 × crash_barrier_base_width + footpath + railing
        return carriageway_width + 2 * crash_barrier_base_width + footpath_width + railing_width
    
    elif footpath_config == "BOTH":
        # carriageway + 2 × crash_barrier_base_width + 2 × footpath + 2 × railing
        return carriageway_width + 2 * crash_barrier_base_width + 2 * footpath_width + 2 * railing_width
    
    else:
        raise ValueError(f"Invalid footpath_config: {footpath_config}")


def build_deck():
    """
    Builds the deck slab based on footpath configuration.
    Deck is always centered at Y=0.
    """
    total_deck_width = calculate_deck_width(footpath_config)
    
    deck = create_deck_slab(
        span_length_L,
        total_deck_width,
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
                        bracket_option=x_bracket_option,
                        section_type=cross_bracing_section_type,
                        section_props=cross_bracing_section_props
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
                        top_bracket=k_top_bracket,
                        section_type=cross_bracing_section_type,
                        section_props=cross_bracing_section_props
                    )
                )

            else:
                raise ValueError(
                    f"Invalid bracing_type '{bracing_type}'. "
                    "Allowed values are 'X' or 'K'."
                )

    return cross_bracings

def calculate_deck_width(footpath_config):
    """
    Calculates total deck width based on footpath configuration.
    
    Returns:
    --------
    total_deck_width : float
    """
    
    if footpath_config == "NONE":
        # carriageway + 2 × crash_barrier_base_width
        return carriageway_width + 2 * crash_barrier_base_width
    
    elif footpath_config == "LEFT" or footpath_config == "RIGHT":
        # carriageway + 2 × crash_barrier_base_width + footpath + railing
        return carriageway_width + 2 * crash_barrier_base_width + footpath_width + railing_width
    
    elif footpath_config == "BOTH":
        # carriageway + 2 × crash_barrier_base_width + 2 × footpath + 2 × railing
        return carriageway_width + 2 * crash_barrier_base_width + 2 * footpath_width + 2 * railing_width
    
    else:
        raise ValueError(f"Invalid footpath_config: {footpath_config}")


def calculate_carriageway_offset(footpath_config):
    """
    Calculates the carriageway position relative to deck center (Y=0).
    
    DECK is always centered at Y=0.
    Carriageway position depends on footpath configuration.
    
    Returns:
    --------
    carriageway_y_offset : float (offset of carriageway center from Y=0)
    """
    
    if footpath_config == "NONE" or footpath_config == "BOTH":
        # Symmetric config - carriageway is centered
        return 0
    
    elif footpath_config == "LEFT":
        # Footpath on left - carriageway shifts RIGHT (positive Y)
        # Shift = (footpath_width + railing_width) / 2
        return (footpath_width + railing_width) / 2
    
    elif footpath_config == "RIGHT":
        # Footpath on right - carriageway shifts LEFT (negative Y)
        # Shift = -(footpath_width + railing_width) / 2
        return -(footpath_width + railing_width) / 2
    
    else:
        raise ValueError(f"Invalid footpath_config: {footpath_config}")
    


def build_crash_barrier(deck_top_z):
    """
    Builds crash barriers based on footpath configuration.
    
    DECK is centered at Y=0.
    Crash barriers are placed relative to deck edges and carriageway position.
    
    Logic:
    - Carriageway position is calculated based on footpath config
    - Crash barriers are placed at carriageway edges
    - If no footpath on a side, crash barrier extends to deck edge
    """
    crash_barriers = []

    # Get deck dimensions
    total_deck_width = calculate_deck_width(footpath_config)
    deck_half_width = total_deck_width / 2
    
    # Get carriageway position (offset from Y=0)
    carriageway_offset = calculate_carriageway_offset(footpath_config)
    carriageway_half_width = carriageway_width / 2
    
    # Calculate carriageway edges in global coordinates
    carriageway_right_edge = carriageway_offset + carriageway_half_width
    carriageway_left_edge = carriageway_offset - carriageway_half_width
    
    # CASE 1: NO FOOTPATH
    # Both barriers at deck edges (carriageway = full deck width)
    if footpath_config == "NONE":
        # Right crash barrier at deck edge
        barrier_right = create_crash_barrier_right(
            length=span_length_L,
            width=crash_barrier_width,
            height=crash_barrier_height,
            base_width=crash_barrier_base_width
        )
        barrier_y_right = deck_half_width - crash_barrier_base_width / 2
        crash_barriers.append(
            place_crash_barrier(
                barrier_right,
                x=0,
                y=barrier_y_right,
                z=deck_top_z
            )
        )
        
        # Left crash barrier at deck edge
        barrier_left = create_crash_barrier_left(
            length=span_length_L,
            width=crash_barrier_width,
            height=crash_barrier_height,
            base_width=crash_barrier_base_width
        )
        barrier_y_left = -deck_half_width + crash_barrier_base_width / 2
        crash_barriers.append(
            place_crash_barrier(
                barrier_left,
                x=0,
                y=barrier_y_left,
                z=deck_top_z
            )
        )
    
    # CASE 2: LEFT FOOTPATH ONLY
    # Left: barrier at carriageway edge (before footpath)
    # Right: barrier at deck edge (no footpath)
    elif footpath_config == "LEFT":
        # Right side: NO footpath → crash barrier at DECK EDGE
        barrier_right = create_crash_barrier_right(
            length=span_length_L,
            width=crash_barrier_width,
            height=crash_barrier_height,
            base_width=crash_barrier_base_width
        )
        barrier_y_right = deck_half_width - crash_barrier_base_width / 2
        crash_barriers.append(
            place_crash_barrier(
                barrier_right,
                x=0,
                y=barrier_y_right,
                z=deck_top_z
            )
        )
        
        # Left side: HAS footpath → crash barrier at CARRIAGEWAY EDGE
        barrier_left = create_crash_barrier_left(
            length=span_length_L,
            width=crash_barrier_width,
            height=crash_barrier_height,
            base_width=crash_barrier_base_width
        )
        barrier_y_left = carriageway_left_edge - crash_barrier_base_width / 2
        crash_barriers.append(
            place_crash_barrier(
                barrier_left,
                x=0,
                y=barrier_y_left,
                z=deck_top_z
            )
        )
    
    # CASE 3: RIGHT FOOTPATH ONLY
    # Left: barrier at deck edge (no footpath)
    # Right: barrier at carriageway edge (before footpath)
    elif footpath_config == "RIGHT":
        # Left side: NO footpath → crash barrier at DECK EDGE
        barrier_left = create_crash_barrier_left(
            length=span_length_L,
            width=crash_barrier_width,
            height=crash_barrier_height,
            base_width=crash_barrier_base_width
        )
        barrier_y_left = -deck_half_width + crash_barrier_base_width / 2
        crash_barriers.append(
            place_crash_barrier(
                barrier_left,
                x=0,
                y=barrier_y_left,
                z=deck_top_z
            )
        )
        
        # Right side: HAS footpath → crash barrier at CARRIAGEWAY EDGE
        barrier_right = create_crash_barrier_right(
            length=span_length_L,
            width=crash_barrier_width,
            height=crash_barrier_height,
            base_width=crash_barrier_base_width
        )
        barrier_y_right = carriageway_right_edge + crash_barrier_base_width / 2
        crash_barriers.append(
            place_crash_barrier(
                barrier_right,
                x=0,
                y=barrier_y_right,
                z=deck_top_z
            )
        )
    
    # CASE 4: BOTH FOOTPATHS
    # Both barriers at carriageway edges (symmetric)
    elif footpath_config == "BOTH":
        # Right crash barrier at carriageway edge
        barrier_right = create_crash_barrier_right(
            length=span_length_L,
            width=crash_barrier_width,
            height=crash_barrier_height,
            base_width=crash_barrier_base_width
        )
        barrier_y_right = carriageway_right_edge + crash_barrier_base_width / 2
        crash_barriers.append(
            place_crash_barrier(
                barrier_right,
                x=0,
                y=barrier_y_right,
                z=deck_top_z
            )
        )

        # Left crash barrier at carriageway edge
        barrier_left = create_crash_barrier_left(
            length=span_length_L,
            width=crash_barrier_width,
            height=crash_barrier_height,
            base_width=crash_barrier_base_width
        )
        barrier_y_left = carriageway_left_edge - crash_barrier_base_width / 2
        crash_barriers.append(
            place_crash_barrier(
                barrier_left,
                x=0,
                y=barrier_y_left,
                z=deck_top_z
            )
        )

    return crash_barriers



def build_railing(deck_top_z):
    """
    Builds railings at DECK EDGES based on footpath configuration.
    Railings only exist where footpaths exist.
    """
    railings = []

    # No railings for NONE case
    if footpath_config == "NONE":
        return railings

    # Create base railing shape
    base_railing = create_railing(
        length=span_length_L,
        width=railing_width,
        height=railing_height,
        rail_count=rail_count
    )

    # Calculate deck edge position
    total_deck_width = calculate_deck_width(footpath_config)
    deck_half_width = total_deck_width / 2

    # LEFT FOOTPATH - Railing at left deck edge
    if footpath_config == "LEFT" or footpath_config == "BOTH":
        railing_y_left = -(deck_half_width - railing_width / 2)
        railings.append(
            place_railing(
                base_railing,
                x=span_length_L / 2,
                y=railing_y_left,
                z=deck_top_z
            )
        )

    # RIGHT FOOTPATH - Railing at right deck edge
    if footpath_config == "RIGHT" or footpath_config == "BOTH":
        railing_y_right = deck_half_width - railing_width / 2
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
    girders, stiffeners = build_girders()
    cross_bracings = build_cross_bracing()
    deck = build_deck()
    deck_top_z = girder_section_d + deck_thickness
    crash_barriers = build_crash_barrier(deck_top_z)
    railings = build_railing(deck_top_z)

    return girders, stiffeners, cross_bracings, deck, crash_barriers, railings



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
    )

    # Calculate dimensions
    total_deck_width = calculate_deck_width(footpath_config)
    carriageway_offset = calculate_carriageway_offset(footpath_config)

    # Print configuration
    print("=" * 60)
    print("BRIDGE CONFIGURATION")
    print("=" * 60)
    print(f"Footpath Configuration: {footpath_config}")
    print(f"Carriageway Width: {carriageway_width} mm")
    if footpath_config in ["LEFT", "RIGHT"]:
        print(f"Carriageway Offset from Center: {carriageway_offset:+.1f} mm")
    print(f"Crash Barrier Base Width: {crash_barrier_base_width} mm")
    if footpath_config != "NONE":
        print(f"Footpath Width: {footpath_width} mm")
        print(f"Railing Width: {railing_width} mm")
    print(f"Total Deck Width: {total_deck_width} mm")
    print(f"\nNumber of Girders: {num_girders}")
    print(f"Girder Spacing: {girder_spacing} mm")
    print("=" * 60)

    # Initialize display
    display, start_display, add_menu, add_function_to_menu = init_display()

    # Assemble bridge components
    girders, stiffeners, cross_bracings, deck, crash_barriers, railings = assemble_bridge()

    # Display girders
    for g in girders:
        display_colored(display, g, COLOR_GIRDER)

    for s in stiffeners:
        display_colored(display, s, COLOR_STIFFENER)

    # Display cross bracings
    for cb in cross_bracings:
        display_colored(display, cb, COLOR_CROSS_BRACING)

    # Display deck slab (CRITICAL)
    display_colored(display, deck, COLOR_DECK)


    # Generate & display deck texture
    deck_top_z = girder_section_d + deck_thickness

    texture_shapes = place_deck_texture(
        deck_length=span_length_L,
        deck_width=total_deck_width,
        deck_thickness=deck_thickness,
        deck_top_z=deck_top_z
    )

    for s in texture_shapes:
        display.DisplayShape(s, color=texture_color, update=False)


    # --------------------------------------------------
    # Display crash barriers
    # --------------------------------------------------
    for cb in crash_barriers:
        display_colored(display, cb, COLOR_CRASH_BARRIER)

    # --------------------------------------------------
    # Display railings
    # --------------------------------------------------
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