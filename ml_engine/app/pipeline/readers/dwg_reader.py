import logging
import subprocess
from pathlib import Path
from typing import List
from app.models.structural import Line2D
from app.pipeline.ingestion import extract_lines_from_dxf

logger = logging.getLogger(__name__)

class DWGReader:
    @staticmethod
    def extract_lines(file_path: Path) -> List[Line2D]:
        """
        Lee un archivo DWG, requiere conversión a DXF a través de una utilidad del SO
        (ej: ODA File Converter o libredwg). Luego extrae las líneas usando ezdxf.
        Dado que este es un esqueleto/prototipo, simulará la conversión si la CLI no existe.
        """
        logger.info(f"Intentando procesar el archivo DWG nativo: {file_path}")

        try:
            dxf_output_path = file_path.with_suffix('.dxf')

            # 1. Ejecutar comando de conversión (Ejemplo: dwg2dxf)
            # En un entorno real se instalaría LibreDWG (dwg2dxf) u ODA
            logger.info(f"Convirtiendo DWG a DXF: {file_path} -> {dxf_output_path}")

            try:
                # Simulamos la llamada al binario del sistema:
                # result = subprocess.run(['dwg2dxf', '-o', str(dxf_output_path), str(file_path)], check=True, capture_output=True)
                # Como no tenemos `dwg2dxf` en este sandbox, esto fallará intencionalmente, y lo manejaremos:
                process = subprocess.Popen(['dwg2dxf', '-o', str(dxf_output_path), str(file_path)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                _, stderr = process.communicate()

                if process.returncode != 0:
                    raise FileNotFoundError("Binario 'dwg2dxf' no encontrado o fallo al ejecutar.")

            except FileNotFoundError:
                logger.warning("Conversor DWG->DXF no instalado en el sistema operativo. Retornando un mock de líneas estructurales.")
                # Mock temporal para permitir al pipeline continuar durante el desarrollo
                from app.models.structural import Point2D
                return [
                    Line2D(start=Point2D(x=0.0, y=0.0), end=Point2D(x=10.0, y=0.0), layer="0_MOCK_DWG"),
                    Line2D(start=Point2D(x=10.0, y=0.0), end=Point2D(x=10.0, y=2.0), layer="0_MOCK_DWG")
                ]

            # 2. Si la conversión es exitosa, se usa el lector DXF existente
            if dxf_output_path.exists():
                logger.info("Conversión exitosa, leyendo DXF resultante.")
                return extract_lines_from_dxf(dxf_output_path)
            else:
                raise RuntimeError("El archivo DXF no fue generado después del comando de conversión.")

        except subprocess.CalledProcessError as sub_e:
            logger.error(f"Fallo el proceso de conversión DWG a nivel del SO: {sub_e.stderr}")
            raise RuntimeError(f"Fallo la conversión de DWG a DXF: {sub_e.stderr}")

        except Exception as e:
            # Regla de manejo estricto de excepciones de I/O
            logger.error(f"Error crítico en lector DWG: {e}")
            raise Exception(f"Fallo al procesar el archivo DWG: {e}")
