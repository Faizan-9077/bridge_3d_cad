# sections/angle_section.py

from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Fuse
from OCC.Core.gp import gp_Trsf, gp_Vec
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Transform


def create_angle_section(length, leg_h, leg_w, thickness):
    """
    Angle section whose centroid is at origin (box-compatible).
    Length along +X.
    """

    # Vertical leg
    leg1 = BRepPrimAPI_MakeBox(
        length,
        thickness,
        leg_h
    ).Shape()

    # Horizontal leg
    leg2 = BRepPrimAPI_MakeBox(
        length,
        leg_w,
        thickness
    ).Shape()

    angle = BRepAlgoAPI_Fuse(leg1, leg2).Shape()


    # Box was centered at (-t/2, -t/2)
    # Angle bounding box is (leg_w, leg_h)

    trsf = gp_Trsf()
    trsf.SetTranslation(
        gp_Vec(
            -length / 2,
            -leg_w / 2,
            -leg_h / 2
        )
    )

    return BRepBuilderAPI_Transform(angle, trsf, True).Shape()
