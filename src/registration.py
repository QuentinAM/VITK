import itk

def image_registration_rigid(fixed_image, moving_image, debug: bool=True):
    imagetype = itk.Image[itk.ctype('float'), 3]

    #define transform type
    TransformType = itk.VersorRigid3DTransform[itk.D]
    initial_transform = TransformType.New()

    #define optimizer
    optimizer = itk.RegularStepGradientDescentOptimizerv4[itk.D].New(
        LearningRate=0.1,
        MinimumStepLength=0.001,
        RelaxationFactor=0.5,
        NumberOfIterations=200,
        ReturnBestParametersAndValue=True
    )

    #define metric
    metric = itk.MeanSquaresImageToImageMetricv4[imagetype, imagetype].New()

    # define de registration method
    registration = itk.ImageRegistrationMethodv4[imagetype,imagetype].New(
        FixedImage=fixed_image, 
        MovingImage=moving_image, 
        Metric=metric,
        Optimizer=optimizer, 
        InitialTransform=initial_transform,
    )
    registration.SetNumberOfLevels(1)
    registration.SetSmoothingSigmasPerLevel([0])
    registration.SetShrinkFactorsPerLevel([1])
    
    TransformInitializerType = itk.CenteredTransformInitializer[TransformType, imagetype, imagetype]
    initializer = TransformInitializerType.New(
        Transform=initial_transform,
        FixedImage=fixed_image,
        MovingImage=moving_image
    )
    initializer.MomentsOn()
    initializer.InitializeTransform()

    optimizer_scales = itk.OptimizerParameters[itk.D](initial_transform.GetNumberOfParameters())

    optimizer_scales[0] = 1.0
    optimizer_scales[1] = 1.0
    optimizer_scales[2] = 1.0
    optimizer_scales[3] = 1.0 / 1000.0
    optimizer_scales[4] = 1.0 / 1000.0
    optimizer_scales[5] = 1.0 / 1000.0

    optimizer.SetScales(optimizer_scales)

    registration.Update()

    transform = registration.GetTransform()
    final_parameters = transform.GetParameters()

    if (debug):
        # Compute debugs information
        angle = final_parameters.GetElement(0)
        translation_along_x = final_parameters.GetElement(1)
        translation_along_y = final_parameters.GetElement(2)
        translation_along_z = final_parameters.GetElement(3)
        number_of_iterations = optimizer.GetCurrentIteration()
        best_value = optimizer.GetValue()
        
        print("Result = ")
        print(" Angle = " + str(angle))
        print(" Translation X = " + str(translation_along_x))
        print(" Translation Y = " + str(translation_along_y))
        print(" Translation Z = " + str(translation_along_z))
        print(" Iterations    = " + str(number_of_iterations))
        print(" Metric value  = " + str(best_value))

    finalTransform = TransformType.New()
    finalTransform.SetFixedParameters(registration.GetOutput().Get().GetFixedParameters())
    finalTransform.SetParameters(registration.GetOutput().Get().GetParameters())

    # Resample the moving image using the final transform to make a 
    resample = itk.ResampleImageFilter[imagetype, imagetype].New()
    resample.SetTransform(finalTransform)
    resample.SetInput(moving_image)
    resample.SetSize(fixed_image.GetLargestPossibleRegion().GetSize())
    resample.SetOutputOrigin(fixed_image.GetOrigin())
    resample.SetOutputSpacing(fixed_image.GetSpacing())
    resample.SetOutputDirection(fixed_image.GetDirection())
    resample.SetDefaultPixelValue(100)
    resample.Update()
    return resample.GetOutput()
    
def image_registration_affine(fixed_image, moving_image, debug: bool=True):
    imagetype = itk.Image[itk.ctype('float'), 3]

    #define transform type
    TransformType = itk.AffineTransform[itk.D, 3]
    initial_transform = TransformType.New()

    #define optimizer
    optimizer = itk.RegularStepGradientDescentOptimizer.New(
        MinimumStepLength=0.001,
        RelaxationFactor=0.5,
        NumberOfIterations=500,
        MaximumStepLength=1.0
    )
    optimizer.MinimizeOn()
    
    #define metric
    metric = itk.MeanSquaresImageToImageMetric[imagetype, imagetype].New()

    #define interpolator
    interpolator = itk.LinearInterpolateImageFunction[imagetype, itk.D].New()

    # define de registration method
    registration = itk.ImageRegistrationMethod[imagetype,imagetype].New(
        FixedImage=fixed_image, 
        MovingImage=moving_image,
        FixedImageRegion=fixed_image.GetBufferedRegion(),
        Interpolator=interpolator,
        Metric=metric,
        Optimizer=optimizer, 
        Transform=initial_transform,
        InitialTransformParameters=initial_transform.GetParameters()
    )

    optimizer_scales = itk.OptimizerParameters[itk.D](initial_transform.GetNumberOfParameters())

    for i in range(9):
        optimizer_scales[i] = 1.0
    optimizer_scales[9] = 1.0 / 1000.0
    optimizer_scales[10] = 1.0 / 1000.0
    optimizer_scales[11] = 1.0 / 1000.0

    optimizer.SetScales(optimizer_scales)
    
    registration.Update()
    
    finalParameters = registration.GetOutput().Get().GetParameters()

    if (debug):
        # Compute debugs information
        maxNumberOfIterations = optimizer.GetCurrentIteration()
        bestValue = optimizer.GetValue()

        print("Result = ")
        print(" Iterations    = " + str(maxNumberOfIterations))
        print(" Metric value  = " + str(bestValue))

    finalTransform = TransformType.New()
    finalTransform.SetParameters(finalParameters)
    finalTransform.SetFixedParameters(initial_transform.GetFixedParameters())

    # Resample the moving image using the final transform to make a 
    resample = itk.ResampleImageFilter[imagetype, imagetype].New()
    resample.SetTransform(finalTransform)
    resample.SetInput(moving_image)
    resample.SetSize(fixed_image.GetLargestPossibleRegion().GetSize())
    resample.SetOutputOrigin(fixed_image.GetOrigin())
    resample.SetOutputSpacing(fixed_image.GetSpacing())
    resample.SetOutputDirection(fixed_image.GetDirection())
    resample.SetDefaultPixelValue(100)
    resample.Update()
    return resample.GetOutput()

def calculate_difference(image1, image2):
    imagetype = itk.Image[itk.F, image1.GetImageDimension()]
    
    resampler = itk.ResampleImageFilter.New(
        Input=image2,
        ReferenceImage=image1,
    )
    resampler.UseReferenceImageOn()
    resampler.Update()

    subtract_filter = itk.SubtractImageFilter[imagetype, imagetype, imagetype].New(
        Input1=image1,
        Input2=resampler.GetOutput()
    )

    abs_diff_filter = itk.AbsImageFilter[imagetype, imagetype].New(
        Input=subtract_filter.GetOutput()
    )
    abs_diff_filter.Update()

    statistics_filter = itk.StatisticsImageFilter[imagetype].New(
        Input=abs_diff_filter.GetOutput()
    )
    statistics_filter.Update()

    return statistics_filter