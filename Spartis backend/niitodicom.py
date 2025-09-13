import os
import SimpleITK as sitk
import pydicom
from pydicom.dataset import FileDataset, FileMetaDataset
import datetime
import numpy as np
import uuid
import nibabel as nib


def fix_nifti_orientation_nibabel(nii_path, fixed_nii_path):
    # Load NIfTI using NiBabel
    nifti = nib.load(nii_path)
    
    # Extract affine transformation matrix
    affine = nifti.affine.copy()

    # Compute nearest orthonormal matrix using SVD
    U, _, Vt = np.linalg.svd(affine[:3, :3])
    affine[:3, :3] = np.dot(U, Vt)  # Enforce orthonormality

    # Create new NIfTI image with corrected affine
    fixed_nifti = nib.Nifti1Image(nifti.get_fdata(), affine, nifti.header)
    
    # Save the corrected image
    nib.save(fixed_nifti, fixed_nii_path)


def generate_dicom_uid():
    return "2.25." + str(uuid.uuid4().int)


def nii_to_dicom(nii_path, dicom_output_dir):
    os.makedirs(dicom_output_dir, exist_ok=True)

    # Load image using SimpleITK (preserves spacing, direction, origin)
    image = sitk.ReadImage(nii_path)
    spacing = image.GetSpacing()
    direction = np.array(image.GetDirection()).reshape(3, 3)
    origin = np.array(image.GetOrigin())
    size = image.GetSize()  # (x, y, z)
    array = sitk.GetArrayFromImage(image)  # (z, y, x)

    print(f"Image size: {size}, spacing: {spacing}")
    if array.shape[0] < 2:
        print("⚠️ ERROR: Only one slice in Z dimension. Mesh generation will fail.")
        return

    # UID generation
    study_uid = generate_dicom_uid()
    series_uid = generate_dicom_uid()
    now = datetime.datetime.now()

    # Orientation vectors
    row_cosines = direction[:, 0]
    col_cosines = direction[:, 1]
    normal_cosines = np.cross(row_cosines, col_cosines)

    for z in range(array.shape[0]):
        pixel_data = array[z].astype(np.int16)

        # Compute ImagePositionPatient using direction cosines
        ipp = origin + z * spacing[2] * normal_cosines

        file_meta = FileMetaDataset()
        file_meta.MediaStorageSOPClassUID = pydicom.uid.CTImageStorage
        file_meta.MediaStorageSOPInstanceUID = generate_dicom_uid()
        file_meta.TransferSyntaxUID = pydicom.uid.ExplicitVRLittleEndian
        file_meta.ImplementationClassUID = generate_dicom_uid()

        ds = FileDataset(None, {}, file_meta=file_meta, preamble=b"\0" * 128)
        ds.PatientName = "Test^Patient"
        ds.PatientID = "123456"
        ds.StudyInstanceUID = study_uid
        ds.SeriesInstanceUID = series_uid
        ds.SOPInstanceUID = file_meta.MediaStorageSOPInstanceUID
        ds.SOPClassUID = file_meta.MediaStorageSOPClassUID
        ds.Modality = "CT"
        ds.StudyDate = now.strftime("%Y%m%d")
        ds.StudyTime = now.strftime("%H%M%S")
        ds.SeriesNumber = 1
        ds.InstanceNumber = z + 1

        # DICOM spatial tags
        ds.Rows, ds.Columns = pixel_data.shape
        ds.PixelSpacing = [str(spacing[1]), str(spacing[0])]  # y, x
        ds.SliceThickness = spacing[2]
        ds.ImagePositionPatient = [str(val) for val in ipp]
        ds.ImageOrientationPatient = [str(val) for val in np.concatenate([row_cosines, col_cosines])]
        ds.SliceLocation = float(ipp[2])
        ds.SamplesPerPixel = 1
        ds.PhotometricInterpretation = "MONOCHROME2"
        ds.BitsAllocated = 16
        ds.BitsStored = 16
        ds.HighBit = 15
        ds.PixelRepresentation = 1
        ds.RescaleIntercept = 0
        ds.RescaleSlope = 1
        ds.PixelData = pixel_data.tobytes()

        out_path = os.path.join(dicom_output_dir, f"slice_{z:04d}.dcm")
        ds.save_as(out_path)
        #print(f"✅ Saved: {out_path}")

    print("\n✅ DICOM series conversion complete.")


# Example usage
if __name__ == "__main__":
    nifti_file = "CTChest_low_modified.nii.gz"          # Replace with your file
    dicom_output = "CTChestnew"   # Replace with your target directory
    nii_to_dicom(nifti_file, dicom_output)
