import itk

def smoothing(image):
    """
    Smooth an image
    """
    smoothing_filter = itk.CurvatureFlowImageFilter.New(image)
    smoothing_filter.SetNumberOfIterations(5)
    smoothing_filter.SetTimeStep(0.125)
    smoothing_filter.Update()
    return smoothing_filter.GetOutput()

def segmentation(image, lower_threshold, upper_threshold,index):
    imageType = itk.Image[itk.F, 3]
    connectedThreshold = itk.ConnectedThresholdImageFilter[imageType, imageType].New()
    connectedThreshold.SetInput(image)
    connectedThreshold.SetLower(lower_threshold)
    connectedThreshold.SetUpper(upper_threshold)
    connectedThreshold.SetReplaceValue(255)
    connectedThreshold.SetSeed(index)
    connectedThreshold.Update()
    return connectedThreshold.GetOutput()