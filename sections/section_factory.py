from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox

from .angle_section import create_angle_section
from .channel_section import create_channel_section
from .double_angle_section import create_double_angle_section
from .double_channel_section import create_double_channel_section


def create_section_solid(
    section_type,
    length,
    thickness,
    section_props=None
):
    """
    Factory for section solids aligned along +X axis.
    """

    if section_type == "BOX":
        return BRepPrimAPI_MakeBox(
            length,
            thickness,
            thickness
        ).Shape()

    elif section_type == "ANGLE":
        return create_angle_section(
            length=length,
            leg_h=section_props["leg_h"],
            leg_w=section_props["leg_w"],
            thickness=section_props["thickness"]
        )

    elif section_type == "DOUBLE_ANGLE":
        return create_double_angle_section(
            length=length,
            leg_h=section_props["leg_h"],
            leg_w=section_props["leg_w"],
            thickness=section_props["thickness"],
            connection_type=section_props.get(
                "connection_type", "LONGER_LEG"
            )
    )



    elif section_type == "CHANNEL":
        return create_channel_section(
            length=length,
            depth=section_props["depth"],
            flange_width=section_props["flange_width"],
            web_thickness=section_props["web_thickness"],
            flange_thickness=section_props["flange_thickness"]
        )
    
    elif section_type == "DOUBLE_CHANNEL":                    
        return create_double_channel_section(
            length=length,
            depth=section_props["depth"],
            flange_width=section_props["flange_width"],
            web_thickness=section_props["web_thickness"],
            flange_thickness=section_props["flange_thickness"]
        )

    else:
        raise ValueError(f"Unsupported section type: {section_type}")
