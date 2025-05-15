README
==========

Extracción de Tablas de PDF a CSV mediante OCR
-------------------------------------------------------

Este proyecto convierte facturas/estados de cuenta (en PDF) a archivos CSV
utilizando técnicas de OCR con **Tesseract** y **OpenCV**.  
El pipeline completo:

1.  Convierte cada página del PDF a imagen (Poppler ― `pdf2image`).
2.  Preprocesa la imagen (CLAHE, filtrado bilateral, umbral adaptativo, cierres
    morfológicos) para realzar texto y líneas.
3.  Aplica OCR con *pytesseract* (`spa+eng`, *OEM 3*, *PSM 6*).
4.  Reconstruye la tabla detectando líneas horizontales a partir de la posición
    vertical de cada palabra y organiza las celdas por columnas.
5.  Une todas las páginas procesadas y guarda el resultado final en CSV.


------------------------------------------------------------------------
Instalación
-----------

1.  Clona o descarga este repositorio.
2.  Crea y activa un entorno virtual (opcional pero recomendado):

    ```
    python -m venv venv
    venv\Scripts\activate   # Windows
    source venv/bin/activate  # Linux/Mac
    ```

3.  Instala las dependencias:

    ```
    pip install -r requirements.txt
    ```

4.  Asegúrate de que:
    * `TESSERACT_PATH` apunte al ejecutable `tesseract.exe`.
    * La variable de entorno `TESSDATA_PREFIX` dirija a la carpeta
      `.../tessdata` con los idiomas `spa.traineddata` y `eng.traineddata`.
    * `POPPLER_PATH` incluya `pdftoppm.exe` y `pdftocairo.exe`.

------------------------------------------------------------------------
Uso rápido
----------

1.  Coloca tus PDFs en la carpeta **data/** (o ajusta la lista
    `pdf_files` en `main()`).
2.  Ejecuta el script principal:

    ```
    python main.py
    ```

3.  El CSV resultante se guarda junto al PDF original (misma ruta, mismo
    nombre, extensión *.csv*).

