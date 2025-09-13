import os
import sys
from pathlib import Path

from isoto1 import process_nifti
from niitodicom2 import fix_nifti_orientation_nibabel, nii_to_dicom
from dicomtomesh import (
    load_dicom_image, dicom_to_mesh, compute_smoothing_params,
    smooth_mesh, save_mesh_as_stl, display_mesh
)

def full_pipeline(
    input_nifti_path,
    output_dir="output",
    threshold=1
):
    os.makedirs(output_dir, exist_ok=True)

    input_path = Path(input_nifti_path)
    base_name = input_path.stem.replace('.nii', '')  # Remove .nii if it exists before .gz
    suffix = input_path.suffix if input_path.suffix != ".gz" else input_path.suffixes[-2]  # Support .nii.gz

    # Step 1: Process
    modified_path = Path(output_dir) / f"{base_name}_processed.nii.gz"
    process_nifti(str(input_path), str(modified_path))

    # Step 2: Fix orientation
    fixed_path = Path(output_dir) / f"{base_name}_fixed.nii.gz"
    fix_nifti_orientation_nibabel(str(modified_path), str(fixed_path))

    # Step 3: Convert to DICOM
    dicom_dir = Path(output_dir) / f"{base_name}_dicom"
    nii_to_dicom(str(fixed_path), str(dicom_dir))

    # Step 4: Load and generate mesh
    volume = load_dicom_image(str(dicom_dir))
    if not volume:
        print("Failed to load DICOM volume.", file=sys.stderr)
        return

    mesh = dicom_to_mesh(volume, threshold)
    if mesh.GetNumberOfCells() == 0:
        print("No mesh could be created. Check threshold or input data.", file=sys.stderr)
        return

    # Step 5: Smooth
    iterations, angle, factor = compute_smoothing_params(mesh)
    smooth_mesh(mesh, iterations, angle, factor)

    # Step 6: Save STL
    stl_path = Path(output_dir) / f"{base_name}_mesh.stl"
    save_mesh_as_stl(mesh, str(stl_path))

    # Step 7: Display
    display_mesh(mesh)

if __name__ == "__main__":
    input_nii = "femur_left.nii.gz"  # Change as needed
    full_pipeline(input_nii)
