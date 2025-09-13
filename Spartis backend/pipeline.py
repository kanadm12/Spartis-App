import os
from pathlib import Path
from isoto1 import process_nifti
from niitodicom import fix_nifti_orientation_nibabel, nii_to_dicom
from dicomtomesh import (
    load_dicom_image, dicom_to_mesh,
    compute_smoothing_params, smooth_mesh, save_mesh_as_stl
)
import nibabel as nib
from nibabel.orientations import aff2axcodes


def not_affine_aligned(nii_path: str) -> bool:
    """
    Checks if the NIfTI file is in standard RAS+ orientation (canonical).
    Returns True if no reorientation is needed.
    """
    img = nib.load(nii_path)
    axcodes = aff2axcodes(img.affine)
    return axcodes == ("R", "A", "S")


def full_pipeline(input_nifti_path: str, output_dir="outputs", threshold=1, file_id=None, progress_callback=None) -> str:
    """
    Runs the entire NIfTI-to-STL pipeline.
    Accepts a `progress_callback(step: str, percent: int)` to emit updates.
    """
    def report(step: str, percent: int):
        if callable(progress_callback):
            progress_callback(step, percent)

    os.makedirs(output_dir, exist_ok=True)

    if not file_id:
        from uuid import uuid4
        file_id = str(uuid4()) 

    input_path = Path(input_nifti_path)
    #base_name = input_path.stem.replace('.nii', '')
    base_name = file_id 
    
    modified_path = Path(output_dir) / f"{base_name}_processed.nii.gz"
    fixed_path = Path(output_dir) / f"{base_name}_fixed.nii.gz"
    dicom_dir = Path(output_dir) / f"{base_name}_dicom"
    stl_path = Path(output_dir) / f"{base_name}_mesh.stl"

    report("Preprocessing NIfTI", 10)
    process_nifti(str(input_path), str(modified_path))

    report("Checking orientation", 20)
    if not_affine_aligned(str(modified_path)):
        report("Fixing orientation", 30)
        fix_nifti_orientation_nibabel(str(modified_path), str(fixed_path))
        nii_path_to_use = str(fixed_path)
    else:
        report("Orientation already correct", 30)
        nii_path_to_use = str(modified_path)
        
    report("Converting to DICOM", 40)
    nii_to_dicom(nii_path_to_use, str(dicom_dir))

    report("Loading DICOM volume", 50)
    volume = load_dicom_image(str(dicom_dir))
    if not volume:
        raise RuntimeError("Failed to load DICOM volume")

    report("Generating mesh", 60)
    mesh = dicom_to_mesh(volume, threshold)
    if mesh.GetNumberOfCells() == 0:
        raise RuntimeError("No mesh could be created. Check threshold.")

    report("Smoothing mesh", 75)
    iterations, angle, factor = compute_smoothing_params(mesh)
    smooth_mesh(mesh, iterations, angle, factor)

    report("Saving STL", 90)
    save_mesh_as_stl(mesh, str(stl_path))

    report("Completed", 100)
    return str(stl_path)
