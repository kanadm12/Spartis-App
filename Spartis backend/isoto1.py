import nibabel as nib
import numpy as np

def process_nifti(nii_path, output_path, bone_threshold=0):
    # Load the NIfTI file
    img = nib.load(nii_path)
    data = img.get_fdata()
    
    # Identify bone regions and set them to 1
    modified_data = np.where(data > bone_threshold, 1, data)
    
    # Create a new NIfTI image
    new_img = nib.Nifti1Image(modified_data, img.affine, img.header)
    
    # Save the modified image
    nib.save(new_img, output_path)
    print(f"Modified NIfTI file saved as: {output_path}")

'''
# Example usage
nii_file = "CTChest_low.nii.gz"  # Replace with your actual file path
output_file = "CTChest_low_modified.nii.gz"
process_nifti(nii_file, output_file)
'''
