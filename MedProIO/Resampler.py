from MedProIO import BaseClasses
import numpy as np
import SimpleITK as sitk

class ResamplerToSpacing(BaseClasses.BaseImageRegistration):
    """
    Resampler class extends BaseImageRegistration for image resampling.
    This class handles the resampling of a moving image to align with a reference image.
    """

    def __init__(self):
        super().__init__()
        self.issues = []  # To keep track of any issues encountered
        self.spacing = (0.5, 0.5, 3.0)
    
    def set_spacing(self, spacing: np.ndarray):
        self.spacing = spacing

    def execute_processing(self):
        """
        Resample images to target resolution spacing. Defaults to (0.5, 0.5, 3.0) mm
        Ref: SimpleITK
        """
        try:
            image = self.reference_image
            spacing = self.spacing

            pad_value = image.GetPixelIDValue()
                # calculate output size in voxels
            out_size = [
                int(np.round(
                    size * (spacing_in / spacing_out)
                ))
                for size, spacing_in, spacing_out in zip(image.GetSize(), image.GetSpacing(), spacing)
            ]
            # set up resampler
            resample = sitk.ResampleImageFilter()
            resample.SetOutputSpacing(list(spacing))
            resample.SetSize(out_size)
            resample.SetOutputDirection(image.GetDirection())
            resample.SetOutputOrigin(image.GetOrigin())
            resample.SetTransform(sitk.Transform())
            resample.SetDefaultPixelValue(pad_value)
            if self.is_binary_mask(image):
                resample.SetInterpolator(sitk.sitkNearestNeighbor)
            else:
                resample.SetInterpolator(sitk.sitkBSpline)
        # perform resampling
            self.transformed_image = resample.Execute(image)

            self.assert_correctness()

        except AssertionError as ee:
            self.issues.append(ee)
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
            assert self.transformed_image.GetSpacing()==self.spacing
        except AssertionError:
            raise AssertionError("Sequence's spacing is not the same with the desired spacing")