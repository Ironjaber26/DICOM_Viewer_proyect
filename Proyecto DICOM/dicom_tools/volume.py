"""Stack a DICOM series (many slices) into a single 3D volume."""

from dataclasses import dataclass
from pathlib import Path
from typing import Tuple, Union

import numpy as np

from .reader import is_dicom_file, load_dicom
from .pixels import get_pixel_array
from .info import DicomInfo, extract_dicom_info

PathLike = Union[str, Path]


@dataclass
class Volume:
    """A 3D stack of slices from a single DICOM series.

    ``array`` has shape ``(num_slices, rows, columns)``, already in
    real units (rescale slope/intercept applied per slice).
    """

    array: np.ndarray
    spacing: Tuple[float, float, float]  # (slice_spacing, row_spacing, col_spacing) in mm
    series_instance_uid: str
    patient_info: DicomInfo

    @property
    def shape(self) -> Tuple[int, int, int]:
        return self.array.shape

    @property
    def is_single_slice(self) -> bool:
        """True for a plain 2D image (no real depth to switch planes)."""
        return self.array.shape[0] <= 1

    def axial(self, index: int) -> np.ndarray:
        """Slice along z (the natural scan direction), shape (rows, cols)."""
        return self.array[index, :, :]

    def coronal(self, index: int) -> np.ndarray:
        """Slice along y (front-to-back), shape (num_slices, cols)."""
        return self.array[:, index, :]

    def sagittal(self, index: int) -> np.ndarray:
        """Slice along x (left-to-right), shape (num_slices, rows)."""
        return self.array[:, :, index]


def _slice_z_position(ds) -> float:
    """Return the z-coordinate used to order slices in the stack.

    Prefers ``ImagePositionPatient`` (the real 3D position, in mm) since
    it's what correctly reconstructs the volume even if slices were
    exported out of order. Falls back to ``InstanceNumber`` if the
    position tag is missing (e.g. non-conformant files).
    """
    position = getattr(ds, "ImagePositionPatient", None)
    if position is not None:
        return float(position[2])
    return float(getattr(ds, "InstanceNumber", 0))


def load_volume(source: PathLike) -> Volume:
    """Load a DICOM path as a 3D volume, auto-detecting what it is:

    - A folder -> one-file-per-slice DICOM series.
    - A single multi-frame file (e.g. "Enhanced" MR/CT storage,
      ultrasound cine loops) -> its frames stacked as a volume.
    - A single plain 2D image -> a 1-slice volume, so the same
      viewer/API works uniformly even when there's nothing to stack.

    Raises
    ------
    ValueError
        If no DICOM files are found in a folder, or if a folder mixes
        more than one ``SeriesInstanceUID`` together.
    """
    source = Path(source)
    if source.is_dir():
        return _load_volume_from_directory(source)
    return _load_volume_from_file(source)


def _load_volume_from_directory(folder: Path) -> Volume:
    datasets = [load_dicom(p) for p in folder.iterdir() if p.is_file() and is_dicom_file(p)]

    if not datasets:
        raise ValueError(f"No se encontraron archivos DICOM en: {folder}")

    series_uids = {str(getattr(ds, "SeriesInstanceUID", "")) for ds in datasets}
    if len(series_uids) > 1:
        raise ValueError(
            f"La carpeta mezcla {len(series_uids)} series distintas "
            f"({folder}); separa cada serie en su propia carpeta."
        )

    datasets.sort(key=_slice_z_position)

    array = np.stack([get_pixel_array(ds) for ds in datasets])

    first, second = datasets[0], datasets[min(1, len(datasets) - 1)]
    z_spacing = abs(_slice_z_position(second) - _slice_z_position(first)) or float(
        getattr(first, "SliceThickness", 1.0)
    )
    pixel_spacing = getattr(first, "PixelSpacing", [1.0, 1.0])
    row_spacing, col_spacing = float(pixel_spacing[0]), float(pixel_spacing[1])

    return Volume(
        array=array,
        spacing=(z_spacing, row_spacing, col_spacing),
        series_instance_uid=str(getattr(first, "SeriesInstanceUID", "")),
        patient_info=extract_dicom_info(first),
    )


def _load_volume_from_file(path: Path) -> Volume:
    ds = load_dicom(path)
    num_frames = int(getattr(ds, "NumberOfFrames", 1) or 1)
    array = get_pixel_array(ds)

    is_multiframe = num_frames > 1 and array.ndim == 3
    if not is_multiframe:
        # Imagen simple de un solo corte: se envuelve como un volumen de
        # profundidad 1 para que el resto del codigo (viewer incluido)
        # no tenga que distinguir "imagen" de "volumen" como casos aparte.
        array = array[np.newaxis, ...]

    # NOTA: los tags de espaciado de "Enhanced" MR/CT en realidad viven
    # por-cuadro dentro de PerFrameFunctionalGroupsSequence; aqui solo
    # se revisan los tags de nivel superior (mas simples, no siempre
    # presentes) y se cae a un espaciado por defecto de 1mm si faltan.
    z_spacing = float(getattr(ds, "SpacingBetweenSlices", None) or getattr(ds, "SliceThickness", None) or 1.0)
    pixel_spacing = getattr(ds, "PixelSpacing", [1.0, 1.0])
    row_spacing, col_spacing = float(pixel_spacing[0]), float(pixel_spacing[1])

    return Volume(
        array=array,
        spacing=(z_spacing, row_spacing, col_spacing),
        series_instance_uid=str(getattr(ds, "SeriesInstanceUID", "")),
        patient_info=extract_dicom_info(ds),
    )
