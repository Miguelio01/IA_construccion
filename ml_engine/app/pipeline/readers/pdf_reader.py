import fitz  # PyMuPDF
import cv2
import pytesseract
import numpy as np
import logging
from pathlib import Path
from typing import List

logger = logging.getLogger(__name__)

class PDFReader:
    @staticmethod
    def extract_text_with_ocr(file_path: Path) -> List[str]:
        """
        Lee un archivo PDF, rasteriza sus páginas a imágenes de alta resolución
        y aplica Tesseract OCR para extraer notas estructurales, cotas y especificaciones.
        Obligatoriamente envuelto en try/except.
        """
        logger.info(f"Iniciando extracción OCR del PDF rasterizado: {file_path}")
        extracted_texts = []

        try:
            # 1. Abrir el documento PDF con PyMuPDF
            doc = fitz.open(file_path)

            for page_num in range(len(doc)):
                page = doc.load_page(page_num)

                # 2. Rasterizar la página: renderizar a imagen para aplicar Computer Vision
                # Establecer una resolución alta (ej. 300 DPI)
                zoom = 3.0
                mat = fitz.Matrix(zoom, zoom)
                pix = page.get_pixmap(matrix=mat, alpha=False)

                # Convertir a arreglo NumPy para OpenCV
                img_data = pix.samples
                # PyMuPDF usa RGB, OpenCV requiere BGR si se usa para procesamiento
                img = np.frombuffer(img_data, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
                if pix.n == 3:
                    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
                elif pix.n == 4:
                    img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)

                # 3. Pre-procesamiento con OpenCV para mejorar el OCR
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                # Binarización simple para resaltar trazos negros del plano
                _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

                # 4. Aplicar Tesseract OCR
                text = pytesseract.image_to_string(binary, lang='eng+spa')
                if text.strip():
                    extracted_texts.append(text.strip())

                logger.info(f"Procesada página {page_num+1}/{len(doc)}")

            doc.close()
            return extracted_texts

        except fitz.FileDataError as fe:
            logger.error(f"El archivo PDF está corrupto o protegido: {fe}")
            raise ValueError(f"No se pudo leer el PDF: {fe}")
        except pytesseract.TesseractNotFoundError as te:
            logger.error(f"Tesseract OCR no está instalado en el sistema operativo: {te}")
            raise RuntimeError("Se requiere instalar el binario 'tesseract' en el SO.")
        except Exception as e:
            # Captura general exigida
            logger.error(f"Fallo crítico durante el procesamiento de visión en PDF: {e}")
            raise RuntimeError(f"Fallo crítico de I/O / OCR en el lector de PDF: {e}")
