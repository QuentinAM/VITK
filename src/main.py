import itk
import time

from compare import *
from registration import *
from segmentation import *
from utils import *
from visualization import *

PRINT_LOG = True
VISUALIZE_BASE_IMAGE = True
VISUALIZE_REGISTERED_IMAGE = True
VISUALIZE_SEGMENTED_IMAGE = True
VISUALIZE_IMAGE_DIFFERENCE = True

if __name__ == "__main__":
    start = time.time()

    # Read files
    image1_path = 'Data/case6_gre1.nrrd'
    image2_path = 'Data/case6_gre2.nrrd'

    if (PRINT_LOG):
        print(f"Reading {image1_path} and {image2_path}...")

    image_1 = read_file(image1_path, itk.Image[itk.ctype('float'), 3])
    image_2 = read_file(image2_path, itk.Image[itk.ctype('float'), 3])

    if (VISUALIZE_BASE_IMAGE):
        visualize_image3D(image_1)
        visualize_image3D(image_2)

    # ########### Registration ###########

    if (PRINT_LOG):
        print("Registering images...")

    # Compute two registration
    registered_image_rigide, time_rigide = time_function(image_registration_rigid, image_1, image_2)
    registered_image_affine, time_affine = time_function(image_registration_affine, image_1, image_2)

    if (VISUALIZE_REGISTERED_IMAGE):
        visualize_image3D(registered_image_rigide)
        visualize_image3D(registered_image_affine)

    if (PRINT_LOG):
        print("Computing differences...")

    # Calculate difference between images
    base_image_diff = calculate_difference(image_1, image_2)
    rigid_image_diff = calculate_difference(image_1, registered_image_rigide)
    affine_image_diff = calculate_difference(image_1, registered_image_affine)
    
    print_image_info("Base Image Difference", base_image_diff)

    print_image_info("\nRigid Image Difference", rigid_image_diff)
    print(f"\nTime taken for rigid registration: {round(time_rigide, 2)}s")
    
    print_image_info("\nAffine Image Difference", affine_image_diff)
    print(f"\nTime taken for affine registration: {round(time_affine, 2)}s")

    # ########### Segmentation ###########

    if (PRINT_LOG):
        print("Smoothing images...")

    # Apply cast filter to resample the image
    cast_filter = itk.CastImageFilter[registered_image_affine, itk.Image[itk.F, 3]].New()
    cast_filter.SetInput(registered_image_affine)
    cast_filter.Update()
    images_2_resampled = cast_filter.GetOutput()
    
    # Smooth both image to have a clean segmentation
    image_1_smoothed = smoothing(image_1)
    images_2_resampled_smoothed = smoothing(images_2_resampled)

    # Segmentation index
    index = [90, 70, 51]

    if (PRINT_LOG):
        print("Segmenting images...")
    
    # Segment the images
    segmented_image_1 = segmentation(image_1_smoothed, 500, 800, index)
    segmented_image_2 = segmentation(images_2_resampled_smoothed, 500, 800, index)

    if (VISUALIZE_SEGMENTED_IMAGE):
        visualize_image3D(segmented_image_1)
        visualize_image3D(segmented_image_2)

    if (VISUALIZE_IMAGE_DIFFERENCE):
        visualize_image_difference(segmented_image_1, segmented_image_2, 50)

    end = time.time()
    print(f"Total time taken: {round(end - start, 2)}s")