import os
import re

import cv2
import numpy as np
import pandas as pd
import pytesseract
from pdf2image import convert_from_path
from pytesseract import Output

POPPLER_PATH = r"C:\poppler-24.08.0\Library\bin"
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
os.environ["TESSDATA_PREFIX"] = r"C:\Program Files\Tesseract-OCR\tessdata"


def enhanced_preprocess_image(image):
    """Preprocesamiento avanzado de imágenes para OCR financiero"""
    try:
        img = np.array(image)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        equalized = clahe.apply(gray)
        denoised = cv2.bilateralFilter(equalized, 9, 75, 75)
        thresh = cv2.adaptiveThreshold(
            denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        kernel = np.ones((2, 2), np.uint8)
        processed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        return processed
    except Exception as e:
        print(f"Error en preprocesamiento: {str(e)}")
        return None


def simple_table_reconstruction(ocr_data, img_width):
    """Reconstrucción simplificada y robusta de tablas"""
    try:
        valid_entries = [
            (i, text, left, top, width, height)
            for i, (text, left, top, width, height) in enumerate(
                zip(
                    ocr_data["text"],
                    ocr_data["left"],
                    ocr_data["top"],
                    ocr_data["width"],
                    ocr_data["height"],
                )
            )
            if text.strip() and int(ocr_data["conf"][i]) > 60
        ]

        if not valid_entries:
            return pd.DataFrame()

        lines = {}
        for _, text, x, y, w, h in valid_entries:
            line_key = y // 10
            if line_key not in lines:
                lines[line_key] = []
            lines[line_key].append((x, text))

        table_data = []
        for y in sorted(lines.keys()):
            sorted_line = sorted(lines[y], key=lambda item: item[0])
            row = [text for x, text in sorted_line]
            table_data.append(row)

        max_cols = max(len(row) for row in table_data) if table_data else 0

        normalized_data = []
        for row in table_data:
            if len(row) < max_cols:
                row += [""] * (max_cols - len(row))
            normalized_data.append(row)

        df = pd.DataFrame(normalized_data)

        df = df.map(lambda x: re.sub(r"\s+", " ", str(x).strip()))

        return df
    except Exception as e:
        print(f"Error en reconstrucción de tabla: {str(e)}")
        return pd.DataFrame()


def process_pdf_to_csv(pdf_path, output_path):
    """Procesa PDF a CSV con manejo robusto de errores"""
    try:
        print(f"\nProcesando {pdf_path}...")

        images = convert_from_path(pdf_path, poppler_path=POPPLER_PATH)
        if not images:
            print(f"No se pudo convertir PDF a imagen: {pdf_path}")
            return False

        all_tables = []
        for i, image in enumerate(images[:1]):
            print(f"Procesando página {i + 1}...")

            processed_img = enhanced_preprocess_image(image)
            if processed_img is None:
                continue

            custom_config = r"--oem 3 --psm 6"
            ocr_data = pytesseract.image_to_data(
                processed_img,
                output_type=Output.DICT,
                config=custom_config,
                lang="spa+eng",
            )

            df = simple_table_reconstruction(ocr_data, processed_img.shape[1])
            if not df.empty:
                all_tables.append(df)

        if not all_tables:
            print(f"No se encontraron tablas en {pdf_path}")
            return False

        final_df = pd.concat(all_tables, ignore_index=True)

        if not output_path.lower().endswith(".csv"):
            output_path = os.path.splitext(output_path)[0] + ".csv"

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        final_df.to_csv(output_path, index=False, encoding="utf-8-sig")

        print(f"Tabla(s) extraída(s) y guardada(s) en: {output_path}")
        return True

    except Exception as e:
        print(f"Error procesando {pdf_path}: {str(e)}")
        return False


def main():
    pdf_files = ["data/1C.PDF", "data/1E.pdf", "data/3T.pdf"]

    for pdf_file in pdf_files:
        if not os.path.exists(pdf_file):
            print(f"\nAdvertencia: {pdf_file} no encontrado, saltando...")
            continue

        output_file = os.path.splitext(pdf_file)[0] + ".csv"
        success = process_pdf_to_csv(pdf_file, output_file)

        if success:
            print(f"Éxito procesando {pdf_file}")
        else:
            print(f"Fallo procesando {pdf_file}")


if __name__ == "__main__":
    main()
