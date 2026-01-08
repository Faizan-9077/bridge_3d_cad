"""
Double Channel Section (Web-to-Web, Opposite Opening)

Resulting shape: ][

- Two C channels
- Webs touch at Y = 0
- One opens +Y, the other opens -Y
- Length along +X
- Centroid lies on Y = 0 plane
"""

from OCC.Core.gp import gp_Trsf, gp_Ax2, gp_Pnt, gp_Dir, gp_Vec
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Fuse

from sections.channel_section import create_channel_section


def create_double_channel_section(
    length,
    depth,
    flange_width,
    web_thickness,
    flange_thickness
):
    """
    Double channel (][) section.

    Geometry convention:
    - Length : +X
    - Width  : ±Y
    - Height : +Z
    - Origin : bounding-box center

    NOTE:
    - Geometry is bounding-box centered
    - NOT centroid-centered
    """

    base = create_channel_section(
        length=length,
        depth=depth,
        flange_width=flange_width,
        web_thickness=web_thickness,
        flange_thickness=flange_thickness
    )

    # Mirror one channel
    mirror = gp_Trsf()
    mirror.SetMirror(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 1, 0)))
    mirrored = BRepBuilderAPI_Transform(base, mirror, True).Shape()

    # Move channels so webs meet at Y = 0
    offset = flange_width / 2

    trsf_pos = gp_Trsf()
    trsf_pos.SetTranslation(gp_Vec(0, +offset, 0))

    trsf_neg = gp_Trsf()
    trsf_neg.SetTranslation(gp_Vec(0, -offset, 0))

    c1 = BRepBuilderAPI_Transform(base, trsf_pos, True).Shape()
    c2 = BRepBuilderAPI_Transform(mirrored, trsf_neg, True).Shape()

    return BRepAlgoAPI_Fuse(c1, c2).Shape()
