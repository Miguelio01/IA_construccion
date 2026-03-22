import ezdxf
import logging
from typing import List, Dict, Union
from pathlib import Path
from pydantic import ValidationError
from app.models.structural import Line2D, Point2D, BeamGeometry
from app.pipeline.readers.pdf_reader import PDFReader

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

class DataIngestionPipeline:
    @staticmethod
    def process_file(file_path: Path) -> Dict[str, Union[List[Line2D], List[str]]]:
        """
        Actúa como un Patrón Factory para enrutar el archivo a su lector correspondiente
        según la extensión. Extrae geometría estructural y texto con notas relevantes.
        """
        logger.info(f"Ruteando archivo para ingesta estructural: {file_path}")
        result = {"lines": [], "text": []}

        try:
            extension = file_path.suffix.lower()

            if extension == '.dxf':
                result["lines"] = extract_lines_from_dxf(file_path)

            elif extension == '.dwg':
                from app.pipeline.readers.dwg_reader import DWGReader
                result["lines"] = DWGReader.extract_lines(file_path)

            elif extension == '.pdf':
                result["text"] = PDFReader.extract_text_with_ocr(file_path)

            else:
                raise ValueError(f"Formato de archivo no soportado en la ingesta: {extension}")

            return result

        except ValueError as ve:
            logger.error(ve)
            raise ve
        except Exception as e:
            # Captura general requerida por el contrato de arquitectura
            logger.error(f"Error general procesando archivo {file_path}: {e}")
            raise Exception(f"Fallo global del pipeline al enrutar y procesar archivo {file_path}: {e}")
