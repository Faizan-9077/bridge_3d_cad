from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCC.Core.gp import gp_Trsf, gp_Vec
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Transform


def _translate(shape, dx=0, dy=0, dz=0):
    trsf = gp_Trsf()
    trsf.SetTranslation(gp_Vec(dx, dy, dz))
    return BRepBuilderAPI_Transform(shape, trsf, True).Shape()


def create_girder_stiffeners(
    *,
    girder_depth,
    girder_flange_thickness,
    girder_web_thickness,
    girder_flange_width,    
    stiffener_width,
    stiffener_length,
    x_offset=0.0
):
    """
    Create rectangular web stiffeners for I-girder.
    Placement is EXACTLY consistent with create_i_section().
    """

    # 1. Height between flanges
    stiffener_height = (
        girder_depth
        - 2 * girder_flange_thickness
    )

    # 2. Base stiffener geometry
    plate = BRepPrimAPI_MakeBox(
        stiffener_length,
        stiffener_width,
        stiffener_height
    ).Shape()

    # 3. Z placement (above bottom flange)
    z_offset = girder_flange_thickness

    # 4. Web faces (from create_i_section logic)
    web_left_face_y = (girder_flange_width - girder_web_thickness) / 2
    web_right_face_y = web_left_face_y + girder_web_thickness

    # 5. LEFT stiffener (touching web left face)
    left = _translate(
        plate,
        dx=x_offset,
        dy=web_left_face_y - stiffener_width,
        dz=z_offset
    )

    # 6. RIGHT stiffener (touching web right face)
    right = _translate(
        plate,
        dx=x_offset,
        dy=web_right_face_y,
        dz=z_offset
    )

    return left, right
