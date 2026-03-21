import ezdxf
import logging
from typing import List
from pathlib import Path
from pydantic import ValidationError
from app.models.structural import Line2D, Point2D, BeamGeometry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_lines_from_dxf(file_path: Path) -> List[Line2D]:
    """
    Extrae la geometría de líneas de un archivo DXF de forma segura.
    """
    logger.info(f"Intentando parsear el archivo DXF: {file_path}")
    lines_extracted = []

    try:
        # 1. Cargar archivo DXF
        doc = ezdxf.readfile(file_path)
        msp = doc.modelspace()

        # 2. Iterar sobre entidades línea
        for e in msp.query('LINE'):
            try:
                line = Line2D(
                    start=Point2D(x=e.dxf.start.x, y=e.dxf.start.y),
                    end=Point2D(x=e.dxf.end.x, y=e.dxf.end.y),
                    layer=e.dxf.layer
                )
                lines_extracted.append(line)
            except ValidationError as ve:
                logger.warning(f"Error de validación Pydantic para la línea {e}: {ve}")

        logger.info(f"Se extrajeron {len(lines_extracted)} líneas exitosamente.")
        return lines_extracted

    except IOError as e:
        logger.error(f"Fallo de I/O al leer {file_path}: {e}")
        raise RuntimeError(f"Fallo de I/O al leer archivo DXF: {e}")
    except ezdxf.DXFStructureError as e:
        logger.error(f"Estructura DXF inválida en {file_path}: {e}")
        raise ValueError(f"El archivo DXF parece estar corrupto o no es válido: {e}")
    except Exception as e:
        # Siempre envolver en try/except según las reglas
        logger.error(f"Error inesperado al parsear DXF: {e}")
        raise Exception(f"Fallo crítico en pipeline de ingesta: {e}")
