import itk
import matplotlib.pyplot as plt
import time

def read_file(file_path: str, image_type):
    """
    Read itk image
    """
    reader = itk.ImageFileReader[image_type].New()
    reader.SetFileName(file_path)
    reader.Update()
    return reader.GetOutput()

def display_images(image1, image2, slice_number):
    """
    Display two images side by side.
    This function is here just to debug for now.
    """
    plt.figure(figsize=(14, 6))
    
    plt.subplot(1, 2, 1)
    plt.imshow(image1[slice_number, :, :], cmap='gray')
    plt.title(f"Slice {slice_number}")
    plt.axis('off')

    plt.subplot(1, 2, 2)
    plt.imshow(image2[slice_number, :, :], cmap='gray')
    plt.title(f"Slice {slice_number}")
    plt.axis('off')
    plt.show()

def print_image_info(title, image):
    print(title)
    print(f"Mean: {image.GetMean()}")
    print(f"Variance: {image.GetVariance()}")
    print(f"Sigma: {image.GetSigma()}")
    print(f"SumOfSquares: {image.GetSumOfSquares()}")
    print(f"Standard Deviation: {image.GetSigma()}")
    print(f"Minimum: {image.GetMinimum()}")
    print(f"Maximum: {image.GetMaximum()}")

def time_function(func, *args):
    """
    Get the time taken to execute a function
    """
    start = time.time()
    res = func(*args)
    end = time.time()
    return res, end - start