# DICOM_Viewer_proyect
This is a simple viewer of DICOM images... simple huh
# DICOM Tools

A simple Python toolkit to read, inspect, anonymize and visualize **DICOM** medical images, built as a biomedical/medical imaging engineering practice project (using `pydicom`, `numpy`, `matplotlib`, `pandas`).

No real patient data included: the project generates its own synthetic DICOM file for tests and demos, avoiding any privacy/data-protection concerns.



## Features

- **Reading**: load any `.dcm` file and validate whether a file is DICOM.
- **Metadata extraction**: a single function (`extract_dicom_info`) that returns the key patient, study, series, equipment and image information, already organized with safe defaults.
- **Pixels**: convert raw stored values to real-world units (e.g. Hounsfield Units) using `RescaleSlope`/`RescaleIntercept`, plus automatic or manual windowing (contrast).
- **Visualization**: display a DICOM image with a title showing its metadata (modality, body region, dimensions).
- **Basic anonymization**: clear the most common direct identifiers (name, ID, dates, institution, physicians) before sharing or analyzing data.
- **Batch analysis**: scan a whole folder of DICOM files and get a summary table (`pandas.DataFrame`), useful for exploring a study/series exported from a PACS.
- **3D volume**: stack all the slices of a DICOM series into a single 3D numpy volume, ordered by real physical position (not just by file name) — works with either a folder of one-file-per-slice DICOMs, or a single multi-frame file (e.g. "Enhanced" MR storage, ultrasound cine loops).
- **Interactive viewer**: scroll through a volume's slices with the mouse wheel and switch between axial/coronal/sagittal plane with the keyboard, with a PACS-style overlay showing name, ID, sex/age, modality, study and institution.

## Project structure

```
dicom_tools/
├── reader.py        # load and validate DICOM files
├── info.py          # extract_dicom_info(): the main metadata function
├── pixels.py         # pixel conversion and windowing
├── viewer.py         # matplotlib visualization (single image and 3D volume)
├── anonymizer.py      # basic anonymization
├── batch.py           # folder scanning -> DataFrame
└── volume.py          # load_volume(): stack a full series into a 3D volume

scripts/generate_sample_dicom.py    # generates a synthetic DICOM (single image) for testing
scripts/generate_sample_series.py   # generates a full synthetic series (several slices) for testing
scripts/dicom_viewer.py              # single viewer: metadata, single image, 3 planes, or interactive exploration
examples/quick_start.py              # full usage demo
tests/                                # unit tests (pytest)
data/sample_dicom/                    # example DICOM (synthetic, not a real patient)
```

## Installation

```bash
pip install -r requirements.txt
pip install -e .
```

The second command installs `dicom_tools` in editable mode, so `import dicom_tools` works no matter where you run your scripts from (terminal, VS Code, etc.).

## Quick start

The whole viewer lives in a single script: **`scripts/dicom_viewer.py`**. With no arguments, it opens a window to pick a file or folder; it auto-detects whether it's a plain image, a multi-frame file, or a full series, and opens the interactive viewer:

```bash
python scripts/dicom_viewer.py
```

Controls in the viewer window: **mouse wheel** = navigate slices, **keys `a`/`c`/`s`** = switch between axial/coronal/sagittal plane (disabled if the image has only one slice).

You can also pass the path directly (skipping the dialog) and pick other modes:

```bash
python scripts/dicom_viewer.py "path/to/file_or_folder"       # interactive viewer, no dialog
python scripts/dicom_viewer.py "path/to/file.dcm" --info       # only prints the metadata (JSON)
python scripts/dicom_viewer.py "path/to/file.dcm" --static     # the 3 planes at once, static
python scripts/dicom_viewer.py "path/to/file.dcm" --static --save planes.png
python scripts/dicom_viewer.py "path/to/file.dcm" --window-center 40 --window-width 400
```

### Using it from code

```python
from dicom_tools import extract_dicom_info

info = extract_dicom_info("data/sample_dicom/ct_sample.dcm")

print(info.modality)          # "CT"
print(info.patient_id)        # "SIM0001"
print(info.rows, info.columns)  # 128 128
print(info.to_dict())         # dict ready for JSON / pandas
```

Generate the sample file (if it doesn't exist yet):

```bash
python scripts/generate_sample_dicom.py
```

Full demo (metadata + anonymization + batch scanning + visualization):

```bash
python examples/quick_start.py
```

Scan a whole folder of DICOMs:

```python
from dicom_tools import scan_directory

df = scan_directory("path/to/folder_with_dicoms")
df.head()
```

Load a full series (several slices) as a 3D volume:

```bash
python scripts/generate_sample_series.py   # generates 20 synthetic sample slices
```

```python
from dicom_tools import load_volume
from dicom_tools.viewer import show_volume_slices

vol = load_volume("data/sample_dicom/series")
print(vol.shape)     # (20, 128, 128) -> (slices, rows, columns)
print(vol.spacing)   # (slice_spacing_mm, row_spacing_mm, col_spacing_mm)

show_volume_slices(vol)   # shows axial, coronal and sagittal at the volume's center
```

Or from the terminal, without writing Python (equivalent to the above): `python scripts/dicom_viewer.py data/sample_dicom/series --static`.

## Tests

```bash
pip install pytest
pytest
```

## Notes on anonymization

`anonymize_dataset` is a teaching implementation that clears the most common direct identifiers (name, ID, birth date, institution, physicians). **It is not a certified** clinical de-identification tool: for research/production use, rely on a validated tool (e.g. RSNA CTP, dcmtk) and confirm the anonymization profile required by your ethics/IRB committee.


