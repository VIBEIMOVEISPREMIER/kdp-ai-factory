from __future__ import annotations
from dataclasses import dataclass
from typing import Literal
TRIM_HEIGHT={"6x9":9.0,"7x10":10.0,"8x10":10.0,"8x11":11.0,"8.5x11":11.0}
@dataclass
class CoverSpec:
    trim_size:str="8.5x11"; pages:int=100; paper:str="white"; binding:str="paperback"; bleed:float=0.125
def spine_width(pages:int,paper:str="white")->float:
    # KDP paperback approximate constants; final publishing calculation should be verified against current KDP specs.
    factor=0.002252 if paper=="white" else 0.0025
    return pages*factor
def cover_dimensions(spec:CoverSpec)->tuple[float,float]:
    if spec.trim_size not in TRIM_HEIGHT: raise ValueError("Formato inválido")
    w=float(spec.trim_size.split("x")[0]); h=TRIM_HEIGHT[spec.trim_size]
    bleed=spec.bleed*2
    return (w*2+spine_width(spec.pages,spec.paper)+bleed,h+bleed)
