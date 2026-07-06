# DICOM_Viewer_proyect
This is a simple viewer of DICOM images... simple huh
# DICOM Tools

Kit sencillo en Python para leer, inspeccionar, anonimizar y visualizar imágenes médicas en formato **DICOM**, construido como práctica de ingeniería biomédica en imágenes médicas (uso de `pydicom`, `numpy`, `matplotlib`, `pandas`).

No incluye datos reales de pacientes: el proyecto genera su propio archivo DICOM sintético para pruebas y demos, evitando cualquier problema de privacidad/habeas data.

## Características

- **Lectura**: cargar cualquier archivo `.dcm` y validar si un archivo es DICOM.
- **Extracción de metadatos**: una sola función (`extract_dicom_info`) que devuelve la información clave del paciente, estudio, serie, equipo e imagen, ya organizada y con valores por defecto seguros.
- **Píxeles**: conversión de los valores crudos a unidades reales (p. ej. Hounsfield Units) aplicando `RescaleSlope`/`RescaleIntercept`, y *windowing* (contraste) automático o manual.
- **Visualización**: mostrar una imagen DICOM con un título con su metadata (modalidad, región anatómica, dimensiones).
- **Anonimización básica**: limpiar los identificadores directos más comunes (nombre, ID, fechas, institución, médicos) antes de compartir o analizar datos.
- **Análisis por lotes**: escanear una carpeta completa de archivos DICOM y obtener una tabla (`pandas.DataFrame`) resumen, útil para explorar un estudio/serie exportado desde un PACS.
- **Volumen 3D**: apilar todos los cortes (slices) de una serie DICOM en un solo volumen 3D de numpy, ordenados por posición física real (no solo por nombre de archivo) — funciona tanto con una carpeta de un archivo por corte, como con un solo archivo multi-frame (ej. RM "Enhanced", cine de ecografía).
- **Visor interactivo**: navegar los cortes de un volumen con la rueda del mouse y cambiar entre plano axial/coronal/sagital con el teclado, con una superposición estilo PACS mostrando nombre, ID, sexo/edad, modalidad, estudio e institución.

## Estructura del proyecto

```
dicom_tools/
├── reader.py        # cargar y validar archivos DICOM
├── info.py          # extract_dicom_info(): la función principal de metadatos
├── pixels.py         # conversión de píxeles y windowing
├── viewer.py         # visualización con matplotlib (imagen unica y volumen 3D)
├── anonymizer.py      # anonimización básica
├── batch.py           # escaneo de carpetas -> DataFrame
└── volume.py          # load_volume(): apilar una serie completa en un volumen 3D

scripts/generate_sample_dicom.py    # genera un DICOM sintético (una sola imagen) para pruebas
scripts/generate_sample_series.py   # genera una serie sintética completa (varios cortes) para pruebas
scripts/show_info.py                 # imprime la metadata de un archivo .dcm desde la terminal
scripts/view_dicom.py                # ver un archivo .dcm (o un cuadro de uno multi-frame) desde la terminal
scripts/view_planes.py               # ver los 3 planos (axial/coronal/sagital) a la vez, estático
scripts/explore_dicom.py             # visor interactivo: navegar cortes y cambiar de plano (por ruta)
scripts/dicom_viewer.py              # LO MAS FACIL: ventana para elegir archivo/carpeta + visor interactivo
examples/quick_start.py              # demo completa de uso
tests/                                # pruebas unitarias (pytest)
data/sample_dicom/                    # DICOM de ejemplo (sintético, no es un paciente real)
```

## Instalación

```bash
pip install -r requirements.txt
pip install -e .
```

El segundo comando instala `dicom_tools` en modo editable, para que `import dicom_tools` funcione sin importar desde dónde ejecutes tus scripts (terminal, VS Code, etc.).

## Uso rápido

La forma más simple de usar todo el proyecto (sin escribir código ni recordar rutas): abre una ventana para elegir un archivo o carpeta, detecta automáticamente si es una imagen simple, un archivo multi-frame o una serie completa, y abre el visor interactivo:

```bash
python scripts/dicom_viewer.py
```

Controles en la ventana del visor: **rueda del mouse** = navegar cortes, **teclas `a`/`c`/`s`** = cambiar entre plano axial/coronal/sagital (deshabilitado si la imagen tiene un solo corte).

### Uso por código

```python
from dicom_tools import extract_dicom_info

info = extract_dicom_info("data/sample_dicom/ct_sample.dcm")

print(info.modality)          # "CT"
print(info.patient_id)        # "SIM0001"
print(info.rows, info.columns)  # 128 128
print(info.to_dict())         # dict listo para JSON / pandas
```

Ver la metadata de cualquier archivo desde la terminal (sin escribir Python):

```bash
python scripts/show_info.py "ruta/a/archivo.dcm"
```

Generar el archivo de ejemplo (si no existe todavía):

```bash
python scripts/generate_sample_dicom.py
```

Demo completa (metadatos + anonimización + escaneo por lotes + visualización):

```bash
python examples/quick_start.py
```

Escanear una carpeta completa de DICOMs:

```python
from dicom_tools import scan_directory

df = scan_directory("ruta/a/carpeta_con_dicoms")
df.head()
```

Visualizar cualquier archivo `.dcm` desde la terminal:

```bash
python scripts/view_dicom.py "ruta/a/archivo.dcm"
python scripts/view_dicom.py "ruta/a/archivo.dcm" --window-center 40 --window-width 400
```

Cargar una serie completa (varios cortes) como un volumen 3D:

```bash
python scripts/generate_sample_series.py   # genera 20 cortes sinteticos de ejemplo
```

```python
from dicom_tools import load_volume
from dicom_tools.viewer import show_volume_slices

vol = load_volume("data/sample_dicom/series")
print(vol.shape)     # (20, 128, 128) -> (cortes, filas, columnas)
print(vol.spacing)   # (espaciado_entre_cortes_mm, alto_pixel_mm, ancho_pixel_mm)

show_volume_slices(vol)   # muestra axial, coronal y sagital del centro del volumen
```

O desde la terminal, sin escribir Python (equivalente a lo anterior):

```bash
python scripts/view_planes.py data/sample_dicom/series
```

Explorar un volumen de forma interactiva (rueda del mouse = navegar cortes, teclas `a`/`c`/`s` = cambiar de plano). Funciona con una carpeta de una serie, un archivo multi-frame, o incluso una imagen simple (en ese caso el cambio de plano queda deshabilitado, ya que no hay más cortes):

```bash
python scripts/explore_dicom.py data/sample_dicom/series
python scripts/explore_dicom.py "C:/ruta/a/un_archivo_multiframe.dcm"
```

O simplemente usa `python scripts/dicom_viewer.py` y elige el archivo/carpeta desde la ventana, sin tener que escribir la ruta en la terminal.

## Pruebas

```bash
pip install pytest
pytest
```

## Notas sobre la anonimización

`anonymize_dataset` es una implementación educativa que limpia los identificadores directos más comunes (nombre, ID, fecha de nacimiento, institución, médicos). **No es una herramienta certificada** de-identificación clínica: para uso en investigación/producción se debe usar una herramienta validada (p. ej. RSNA CTP, dcmtk) y confirmar el perfil de anonimización exigido por el comité de ética/IRB correspondiente.

## Motivación

Proyecto de práctica para aplicar y demostrar manejo de imágenes DICOM en el contexto de una postulación como ingeniero biomédico en imágenes médicas.
