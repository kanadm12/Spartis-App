import vtk

def load_stl(file_path):
    reader = vtk.vtkSTLReader()
    reader.SetFileName(file_path)
    reader.Update()
    return reader.GetOutput()

def display_mesh(mesh):
    print("Displaying mesh...")
    renderer = vtk.vtkRenderer()
    render_window = vtk.vtkRenderWindow()
    render_window.AddRenderer(renderer)
    render_window.SetSize(1000, 800)
    
    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(render_window)
    
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(mesh)
    
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(0.8, 0.8, 0.8)
    actor.GetProperty().SetOpacity(1.0)
    renderer.AddActor(actor)
    
    style = vtk.vtkInteractorStyleTrackballCamera()
    interactor.SetInteractorStyle(style)
    
    renderer.SetBackground(0.1, 0.1, 0.1)
    render_window.Render()
    interactor.Start()

def view_stl(file_path: str):
    mesh = load_stl(file_path)
    display_mesh(mesh)

#view_stl("./outputs/e33db7c0-3de7-458e-a95a-e4f7ce03deb6_CTChest_low_mesh.stl")