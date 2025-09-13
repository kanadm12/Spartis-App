import vtk
import sys
import numpy as np
import nibabel as nib



def load_dicom_image(dicom_dir):
    """
    Loads a DICOM image series from a given directory using VTK.
    :return: vtkImageData object containing the loaded volume
    """
    print(f"Reading DICOM images from: {dicom_dir}")

    reader = vtk.vtkDICOMImageReader()
    reader.SetDirectoryName(dicom_dir)
    reader.Update()

    raw_volume_data = vtk.vtkImageData()
    raw_volume_data.DeepCopy(reader.GetOutput())

    spacing = raw_volume_data.GetSpacing()
    dimensions = raw_volume_data.GetDimensions()
    origin = raw_volume_data.GetOrigin()
    print(f"VTK Detected spacing: {spacing}")
    print(f"Volume dimensions: {dimensions}")
    print(f"Volume origin: {origin}")

    if dimensions == (0, 0, 0):
        print("No DICOM data found in directory!")
        return None

    return raw_volume_data



def dicom_to_mesh(image_data, threshold):
    """
    Converts a DICOM volume (vtkImageData) into a 3D mesh using Marching Cubes.

    :param image_data: vtkImageData object containing the loaded DICOM volume
    :param threshold: Lower threshold for mesh generation
    :param use_upper_threshold: Whether to apply an upper threshold
    :param upper_threshold: Upper threshold value if enabled
    :return: vtkPolyData object containing the generated mesh
    """
    '''
    if use_upper_threshold:
        print(f"Creating surface mesh with iso value range = {threshold} to {upper_threshold}")

        # Apply upper threshold filtering
        image_threshold = vtk.vtkImageThreshold()
        image_threshold.SetInputData(image_data)
        image_threshold.ThresholdByUpper(upper_threshold)
        image_threshold.ReplaceInOn()
        image_threshold.SetInValue(threshold - 1)  # Mask voxels below lower threshold
        image_threshold.Update()

        image_data.DeepCopy(image_threshold.GetOutput())
    else:
    '''
    print(f"Creating surface mesh with iso value = {threshold}")

    # Apply Marching Cubes algorithm
    surface_extractor = vtk.vtkMarchingCubes()
    surface_extractor.SetInputData(image_data)
    surface_extractor.ComputeNormalsOn()
    surface_extractor.SetValue(0, threshold)  # Set isovalue
    surface_extractor.Update()

    # Extract mesh
    mesh = vtk.vtkPolyData()
    mesh.DeepCopy(surface_extractor.GetOutput())

    print("Mesh generation complete.")
    return mesh

def apply_affine_transform_to_mesh(mesh, affine_matrix):
    """
    Applies the full 4x4 affine transformation matrix to a vtkPolyData mesh.
    This correctly maps the mesh from voxel to world coordinates.
    """
    vtk_matrix = vtk.vtkMatrix4x4()
    for i in range(4):
        for j in range(4):
            vtk_matrix.SetElement(i, j, affine_matrix[i, j])

    transform = vtk.vtkTransform()
    transform.SetMatrix(vtk_matrix)

    transform_filter = vtk.vtkTransformPolyDataFilter()
    transform_filter.SetInputData(mesh)
    transform_filter.SetTransform(transform)
    transform_filter.Update()

    transformed_mesh = vtk.vtkPolyData()
    transformed_mesh.DeepCopy(transform_filter.GetOutput())
    return transformed_mesh


def save_mesh_as_stl(mesh, output_path):
    """
    Saves a vtkPolyData mesh as an STL file.

    :param mesh: vtkPolyData object containing the generated mesh
    :param output_path: Path to save the STL file
    """
    stl_writer = vtk.vtkSTLWriter()
    stl_writer.SetFileName(output_path)
    stl_writer.SetInputData(mesh)
    stl_writer.Write()
    print(f"STL file saved at: {output_path}")

def smooth_mesh(mesh, nbr_of_smoothing_iterations, feature_angle, relaxation_factor):
    print(f"Mesh smoothing with {nbr_of_smoothing_iterations} iterations.")

    # Step 1: Ensure the mesh is triangulated
    triangulate = vtk.vtkTriangleFilter()
    triangulate.SetInputData(mesh)
    triangulate.Update()

    # Step 2: Reduce unnecessary complexity using DecimatePro (Limit reduction)
    decimate = vtk.vtkDecimatePro()
    decimate.SetInputData(triangulate.GetOutput())
    decimate.SetTargetReduction(0.1)  # Reduce only 10% to preserve topology
    decimate.PreserveTopologyOn()
    decimate.Update()

    # Step 3: Compute Normals for accurate smoothing
    normals = vtk.vtkPolyDataNormals()
    normals.SetInputData(decimate.GetOutput())
    normals.ComputePointNormalsOn()
    normals.ComputeCellNormalsOn()
    normals.SplittingOff()  # Avoid unwanted artifacts
    normals.Update()

    # Step 4: First pass - Laplacian smoothing (gentle smoothing)
    smoother1 = vtk.vtkSmoothPolyDataFilter()
    smoother1.SetInputData(normals.GetOutput())
    smoother1.SetNumberOfIterations(nbr_of_smoothing_iterations // 2)  # Less aggressive
    smoother1.SetRelaxationFactor(relaxation_factor)  # Adjustable smoothing strength
    smoother1.FeatureEdgeSmoothingOff()  # Keep edges intact
    smoother1.BoundarySmoothingOn()
    smoother1.Update()

    # Step 5: Second pass - Windowed Sinc smoothing (for finer details)
    smoother2 = vtk.vtkWindowedSincPolyDataFilter()
    smoother2.SetInputData(smoother1.GetOutput())
    smoother2.SetNumberOfIterations(nbr_of_smoothing_iterations // 2)
    smoother2.BoundarySmoothingOn()
    smoother2.FeatureEdgeSmoothingOn()
    smoother2.SetFeatureAngle(feature_angle)  # Preserve sharper edges
    smoother2.SetPassBand(0.05)  # Reduced pass band for finer smoothing
    smoother2.NormalizeCoordinatesOn()
    smoother2.Update()

    # Step 6: Recompute Normals (Final Refinement)
    final_normals = vtk.vtkPolyDataNormals()
    final_normals.SetInputData(smoother2.GetOutput())
    final_normals.ComputePointNormalsOn()
    final_normals.ComputeCellNormalsOn()
    final_normals.Update()

    # Copy back to original mesh
    mesh.DeepCopy(final_normals.GetOutput())

    print(f"Smoothing complete with feature angle: {feature_angle} and relaxation factor: {relaxation_factor}.")

def compute_smoothing_params(mesh):
    # Compute basic properties
    num_points = mesh.GetNumberOfPoints()
    num_faces = mesh.GetNumberOfCells()
    
    # Compute mean edge length
    edge_lengths = []
    edges = vtk.vtkExtractEdges()
    edges.SetInputData(mesh)
    edges.Update()
    edge_poly = edges.GetOutput()
    
    for i in range(edge_poly.GetNumberOfCells()):
        pts = edge_poly.GetCell(i).GetPoints()
        if pts.GetNumberOfPoints() == 2:
            p1 = pts.GetPoint(0)
            p2 = pts.GetPoint(1)
            edge_lengths.append(vtk.vtkMath.Distance2BetweenPoints(p1, p2) ** 0.5)
    
    avg_edge_length = sum(edge_lengths) / len(edge_lengths) if edge_lengths else 1.0
    
    # Compute curvature by estimating normal variation
    normals = vtk.vtkPolyDataNormals()
    normals.SetInputData(mesh)
    normals.ComputePointNormalsOn()
    normals.ComputeCellNormalsOn()
    normals.Update()
    
    normal_poly = normals.GetOutput()
    normal_data = normal_poly.GetPointData().GetNormals()
    
    curvature_values = []
    for i in range(1, num_points):
        n1 = normal_data.GetTuple3(i - 1)
        n2 = normal_data.GetTuple3(i)
        curvature_values.append(vtk.vtkMath.AngleBetweenVectors(n1, n2))
    
    median_curvature = sorted(curvature_values)[len(curvature_values) // 2] if curvature_values else 30.0
    '''
    If a mesh has a mix of flat and sharp areas, the median curvature reflects the dominant smooth regions while ignoring isolated sharp edges.
    '''
    
    # Define heuristics for automatic parameter selection
    nbr_of_smoothing_iterations = max(10, min(50, num_faces // 1000))
    feature_angle = max(20, min(80, median_curvature))
    relaxation_factor = max(0.1, min(0.5, avg_edge_length / 10))
    
    return nbr_of_smoothing_iterations, feature_angle, relaxation_factor

# Example usage
# mesh = vtk.vtkPolyData()  # Assume you have a mesh
# iterations, angle, factor = compute_smoothing_params(mesh)
# print(f"Computed params -> Iterations: {iterations}, Feature Angle: {angle}, Relaxation Factor: {factor}")


def display_mesh(mesh):
    """
    Displays the generated 3D mesh interactively.
    """
    print("Displaying mesh...")
    renderer = vtk.vtkRenderer()
    render_window = vtk.vtkRenderWindow()
    render_window.AddRenderer(renderer)
    render_window.SetSize(1000, 800)
    
    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(render_window)
    
    # Mapper
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(mesh)
    
    # Actor
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(0.8, 0.8, 0.8)
    renderer.AddActor(actor)
    
    # Interaction
    style = vtk.vtkInteractorStyleTrackballCamera()
    interactor.SetInteractorStyle(style)
    
    renderer.SetBackground(0.1, 0.1, 0.1)
    render_window.Render()
    interactor.Start()


'''
dicom_path = "CTChestnew"
output_stl_path = "chestmod.stl"
threshold_value = 1  


# Load DICOM data
volume = load_dicom_image(dicom_path)

if volume:
    # Convert to mesh
    print("I have volume")
    mesh = dicom_to_mesh(volume, threshold_value)

    if mesh.GetNumberOfCells() == 0:
        print("No mesh could be created. Wrong DICOM or wrong iso value", file=sys.stderr)
        sys.exit(-1)


    iterations, angle, factor = compute_smoothing_params(mesh)
    print(f"Computed params -> Iterations: {iterations}, Feature Angle: {angle}, Relaxation Factor: {factor}")

    smooth_mesh(mesh, iterations, angle, factor)


    #The relaxation factor in the vtkSmoothPolyDataFilter controls the strength of the smoothing operation. 
    #Specifically, it determines how much each vertex is moved toward the average position of its neighboring vertices in each iteration.
    #For sharp structures: featureAngle = 20, relaxationFactor = 0.2
    #for general meshes: featureAngle = 30, relaxationFactor = 0.3
    #For aggressive smoothing: featureAngle = 45, relaxationFactor = 0.5


    display_mesh(mesh)

    # Save as STL
    save_mesh_as_stl(mesh, output_stl_path)
'''
