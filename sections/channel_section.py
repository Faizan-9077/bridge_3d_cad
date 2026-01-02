# sections/channel_section.py

from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Fuse
from OCC.Core.gp import gp_Trsf, gp_Vec
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Transform


def create_channel_section(length, depth, flange_width, web_thickness, flange_thickness):
    """
    Channel (C) section whose centroid is at origin (BOX-compatible).
    
    Geometry convention:
    - Length along +X
    - Web vertical (Z)
    - Flanges along Y
    """


    # 1. Web (vertical plate)

    web = BRepPrimAPI_MakeBox(
        length,
        web_thickness,
        depth
    ).Shape()


    # 2. Bottom flange

    bottom_flange = BRepPrimAPI_MakeBox(
        length,
        flange_width,
        flange_thickness
    ).Shape()

    trsf_bottom = gp_Trsf()
    trsf_bottom.SetTranslation(
        gp_Vec(
            0,
            0,
            0
        )
    )
    bottom_flange = BRepBuilderAPI_Transform(
        bottom_flange, trsf_bottom, True
    ).Shape()


    # 3. Top flange

    top_flange = BRepPrimAPI_MakeBox(
        length,
        flange_width,
        flange_thickness
    ).Shape()

    trsf_top = gp_Trsf()
    trsf_top.SetTranslation(
        gp_Vec(
            0,
            0,
            depth - flange_thickness
        )
    )
    top_flange = BRepBuilderAPI_Transform(
        top_flange, trsf_top, True
    ).Shape()


    # 4. Fuse all parts
  
    channel = BRepAlgoAPI_Fuse(web, bottom_flange).Shape()
    channel = BRepAlgoAPI_Fuse(channel, top_flange).Shape()



    # Bounding box:
    #   Y: flange_width
    #   Z: depth

    trsf_center = gp_Trsf()
    trsf_center.SetTranslation(
        gp_Vec(
            -length / 2,
            -flange_width / 2,
            -depth / 2
        )
    )

    return BRepBuilderAPI_Transform(
        channel, trsf_center, True
    ).Shape()
