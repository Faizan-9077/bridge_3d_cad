# Railing with internal rectangular holes

from draw_rectangular_prism import create_rectangular_prism

from OCC.Core.gp import gp_Vec, gp_Trsf
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Cut, BRepAlgoAPI_Fuse


# Utility
def translate(shape, x=0, y=0, z=0):
    trsf = gp_Trsf()
    trsf.SetTranslation(gp_Vec(x, y, z))
    return BRepBuilderAPI_Transform(shape, trsf, True).Shape()


# Railing geometry
def create_railing(
    length,
    width,
    height,
    rail_count
):
    """
    Railing composed of:
    - Solid base (fixed 100 mm)
    - Upper railing body
    - Rectangular holes inside body at equal vertical spacing
    """

    # Fixed base height
    BASE_HEIGHT = 100  

    body_height = height - BASE_HEIGHT
    if body_height <= 0:
        raise ValueError("Railing height must be greater than base height")

    # 1. Base (solid)
    base = create_rectangular_prism(
        length,
        width,
        BASE_HEIGHT
    )

    # 2. Railing body 
    body = create_rectangular_prism(
        length,
        width,
        body_height
    )

    body = translate(body, z=BASE_HEIGHT)

    # 3. Hole parameters 
    HOLE_LENGTH_RATIO = 1  
    HOLE_WIDTH_RATIO  = 0.6   # smaller than railing width
    HOLE_HEIGHT_RATIO = 0.5   

    hole_length = HOLE_LENGTH_RATIO * length
    hole_width  = HOLE_WIDTH_RATIO  * width
    hole_height = HOLE_HEIGHT_RATIO * (body_height / rail_count)

    # Equal vertical spacing
    spacing = body_height / (rail_count + 1)

    body_with_holes = body

    # 4. Create & cut holes
    for i in range(rail_count):

        z_center = BASE_HEIGHT + (i + 1) * spacing

        HOLE_Y_OFFSET_RATIO = -0.2

        y_offset = HOLE_Y_OFFSET_RATIO * width




        hole = create_rectangular_prism(
            hole_length,
            hole_width,
            hole_height
        )

        hole = translate(
            hole,
            x=(length - hole_length) / 2,   # center in X
            y=(width  - hole_width)  / 2 + y_offset,   # center in Y
            z=z_center - hole_height / 2    # center in Z
        )

        body_with_holes = BRepAlgoAPI_Cut(
            body_with_holes,
            hole
        ).Shape()

    # 5. Fuse base + body
    railing = BRepAlgoAPI_Fuse(
        base,
        body_with_holes
    ).Shape()

    return railing


# Placement
def place_railing(railing, x=0, y=0, z=0):
    return translate(
        railing,
        x=x,
        y=y,
        z=z
    )
