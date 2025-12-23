# barrier_railing.py
# This file will contain crash barrier and railing components

from draw_rectangular_prism import create_rectangular_prism

from OCC.Core.gp import gp_Vec, gp_Trsf
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Transform


def translate(shape, x=0, y=0, z=0):
    trsf = gp_Trsf()
    trsf.SetTranslation(gp_Vec(x, y, z))
    return BRepBuilderAPI_Transform(shape, trsf, True).Shape()

def create_railing(length, width, height):
    
    railing = create_rectangular_prism(
        length,
        width,
        height
    )
    return railing

def place_railing(barrier, x=0, y=0, z=0):
    
    placed_railing = translate(
        barrier,
        x=x,
        y=y,
        z=z
    )
    return placed_railing

