from MedProIO import BaseClasses
import SimpleITK as sitk
import numpy as np

class SequenceResampler(BaseClasses.BaseImageRegistration):
    """
    Resampler class extends BaseImageRegistration for image resampling.
    This class handles the resampling of a moving image to align with a reference image.
    """

    def __init__(self):
        super().__init__()
        self.issues = []  # To keep track of any issues encountered

    def execute_processing(self):
        """
        Resamples the moving image to align with the reference image without taking any arguments.
        The reference and moving images are assumed to be set prior to this method being called.
        """
        try:
            if self.reference_image is None or self.moving_image is None:
                raise ValueError("Reference and/or moving image not set.")

            resample = sitk.ResampleImageFilter()
            ref_original_spacing = self.reference_image.GetSpacing()
            ref_original_size = self.reference_image.GetSize()

            xr, yr, zr = ref_original_size[::-1]

            mov_original_spacing = self.moving_image.GetSpacing()
            mov_original_size = self.moving_image.GetSize()
            mov_pad_value = self.moving_image.GetPixelIDValue()

            mov_out_size = [
                int(np.round(size * (spacing_in / spacing_out)))
                for size, spacing_in, spacing_out in zip(mov_original_size, mov_original_spacing, ref_original_spacing)
            ]

            resample.SetOutputSpacing(ref_original_spacing)
            resample.SetOutputDirection(self.reference_image.GetDirection())
            resample.SetOutputOrigin(self.reference_image.GetOrigin())
            resample.SetTransform(sitk.Transform())
            resample.SetSize(mov_out_size)
            resample.SetDefaultPixelValue(mov_pad_value)

            if self.is_binary_mask(self.moving_image):
                resample.SetInterpolator(sitk.sitkNearestNeighbor)
            else:
                resample.SetInterpolator(sitk.sitkBSpline)


            mov = resample.Execute(self.moving_image)
            mov = sitk.GetArrayFromImage(mov)
            pad_mov = np.zeros((xr, yr, zr))
            xm, ym, zm = mov.shape
            x, y, z = np.min(np.vstack(((xr, yr, zr), (xm, ym, zm))), axis=0)
            pad_mov[:x, :y, :z] = mov[:x, :y, :z]

            mov = sitk.GetImageFromArray(pad_mov)
            mov.CopyInformation(self.reference_image)
            self.transformed_image = mov  # Set the transformed (resampled) image

            self.assert_correctness()

        except AssertionError:
            self.issues.append("Reference & Moving SimpleITK images were not co-registered properly.")
        except ValueError as e:
            self.issues.append(str(e))
        except Exception as e:
            self.issues.append(f"Unexpected error: {e}")

    @staticmethod
    def is_binary_mask(image):
        """
        Determines if the given image is a binary mask.
        
        :param image: SimpleITK image.
        :return: True if the image is a binary mask, False otherwise.
        """
        img_array = sitk.GetArrayFromImage(image)
        return np.all(np.isin(img_array, [0, 1])) or np.all(np.isin(img_array, [0, 1, 2])) 

    def assert_correctness(self):
        """
        Asserts the correctness of the resampling by checking the metadata.
        """
        try:
            assert self.reference_image.GetSpacing() == self.transformed_image.GetSpacing()
            assert self.reference_image.GetDirection() == self.transformed_image.GetDirection()
            assert self.reference_image.GetSize() == self.transformed_image.GetSize()
            assert self.reference_image.GetOrigin() == self.transformed_image.GetOrigin()
        except AssertionError:
            raise AssertionError("Reference and Moving SimpleITK images do not have matching metadata after the registration.")