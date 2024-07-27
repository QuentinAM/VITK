import itk
import vtk

def numpy_to_vtk(numpy_array):
    """
    Convert a numpy array to VTK image
    """
    depthArray = numpy_array.transpose(2, 1, 0).copy()
    res = vtk.vtkImageData()
    res.SetDimensions(depthArray.shape)
    res.AllocateScalars(vtk.VTK_FLOAT, 1)
    
    # Fill array
    for z in range(depthArray.shape[2]):
        for y in range(depthArray.shape[1]):
            for x in range(depthArray.shape[0]):
                res.SetScalarComponentFromFloat(x, y, z, 0, depthArray[x, y, z])
    return res

def visualize_image3D(image):
    """
    Visualize a 3D image
    """
    image_array = itk.GetArrayViewFromImage(image)
    vtk_image = numpy_to_vtk(image_array)

    # Create window and renderer
    renderer = vtk.vtkRenderer()
    window = vtk.vtkRenderWindow()
    window.AddRenderer(renderer)

    # Add interactor to be able to move the camera
    interactor = vtk.vtkRenderWindowInteractor()
    window.SetInteractor(interactor)

    contour = vtk.vtkContourFilter()
    contour.SetInputData(vtk_image)
    contour.SetValue(0, 135)

    contourMapper = vtk.vtkPolyDataMapper()
    contourMapper.SetInputConnection(contour.GetOutputPort())
    contourMapper.ScalarVisibilityOff()

    contourActor = vtk.vtkActor()
    contourActor.SetMapper(contourMapper)

    renderer.AddActor(contourActor)

    window.Render()
    interactor.Start()