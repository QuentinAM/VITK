import itk
import numpy as np
import matplotlib.pyplot as plt

def calculate_dice_similarity(image1, image2):
    arr1 = itk.array_from_image(image1)
    arr2 = itk.array_from_image(image2)

    intersection = np.logical_and(arr1, arr2)
    dice_coefficient = 2.0 * intersection.sum() / (arr1.sum() + arr2.sum())

    return dice_coefficient

def calculate_volume_difference(image1, image2):
    arr1 = itk.array_from_image(image1)
    arr2 = itk.array_from_image(image2)

    voxel_volume = image1.GetSpacing()[0] * image1.GetSpacing()[1] * image1.GetSpacing()[2]

    volume1 = arr1.sum() * voxel_volume
    volume2 = arr2.sum() * voxel_volume
    diff_volume = volume2 - volume1

    return volume1, volume2, diff_volume

def calculate_intensity_difference(image1, image2):
    arr1 = itk.array_from_image(image1)
    arr2 = itk.array_from_image(image2)

    diff_intensity = np.abs(arr2 - arr1).mean()

    return diff_intensity

def visualize_image_difference(image1, image2, slice_number):
    arr1 = itk.array_view_from_image(image1)
    arr2 = itk.array_view_from_image(image2)

    diff = np.abs(arr2 + arr1)

    plt.figure(figsize=(8, 8))
    plt.imshow(diff[slice_number, :, :], cmap='gray')
    plt.axis('off')
    plt.title('Difference between Image 1 and Image 2')
    plt.show()