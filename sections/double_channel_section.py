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
    Creates a web-connected double channel section.

    Geometry rules:
    - Channel length along +X
    - Webs touch at Y = 0
    - Channels open outward
    """


    # 1. Base channel (opens +Y)

    normal = create_channel_section(
        length=length,
        depth=depth,
        flange_width=flange_width,
        web_thickness=web_thickness,
        flange_thickness=flange_thickness
    )

  
    # 2. Mirror channel (opens -Y)

    mirror_trsf = gp_Trsf()
    mirror_trsf.SetMirror(
        gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 1, 0))
    )

    mirrored = BRepBuilderAPI_Transform(
        normal, mirror_trsf, True
    ).Shape()


    # 3. Move channels so WEB faces meet at Y = 0

    y_web_face = -flange_width / 2 + web_thickness

    # Normal channel → right side
    trsf_normal = gp_Trsf()
    trsf_normal.SetTranslation(gp_Vec(0, -y_web_face, 0))
    normal = BRepBuilderAPI_Transform(
        normal, trsf_normal, True
    ).Shape()

    # Mirrored channel → left side
    trsf_mirror = gp_Trsf()
    trsf_mirror.SetTranslation(gp_Vec(0, +y_web_face, 0))
    mirrored = BRepBuilderAPI_Transform(
        mirrored, trsf_mirror, True
    ).Shape()

    # 4. Fuse into single solid

    section = BRepAlgoAPI_Fuse(
        normal, mirrored
    ).Shape()

    return section
