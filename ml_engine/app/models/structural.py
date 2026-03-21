from pydantic import BaseModel, Field
from typing import List, Tuple

class Point2D(BaseModel):
    x: float
    y: float

class Line2D(BaseModel):
    start: Point2D
    end: Point2D
    layer: str = Field(..., description="La capa del archivo CAD donde se encuentra la línea")

class RebarDetails(BaseModel):
    diameter: float = Field(..., description="Diámetro de la varilla (ej. en mm)")
    quantity: int = Field(..., description="Cantidad de varillas")

class BeamGeometry(BaseModel):
    id: str = Field(..., description="Identificador único de la viga")
    lines: List[Line2D] = Field(default_factory=list, description="Topología y contorno de la viga")
    rebars: List[RebarDetails] = Field(default_factory=list, description="Detalles de acero extraídos")
