import SimpleITK as sitk
from MedProIO import BaseClasses
import numpy as np

class AlignmentRegistration(BaseClasses.BaseImageRegistration):
    """
    A class that extends BaseImageRegistration for advanced alignment using SimpleITK.
    This class handles the alignment of two MRI sequences.
    """

    def __init__(self):
        super().__init__()
        self.issues = []  # To keep track of any issues encountered
        self.final_transform = None  # Store the final transformation

    def execute_processing(self):
        """
        Executes the registration of the reference image and moving image.
        """
        try:
            if self.reference_image is None or self.moving_image is None:
                raise ValueError("Reference and/or moving image not set.")

            reference_image_float = sitk.Cast(self.reference_image, sitk.sitkFloat32)
            moving_image_float = sitk.Cast(self.moving_image, sitk.sitkFloat32)

            if self.is_binary_mask(moving_image_float) or self.is_binary_mask(reference_image_float):
                raise TypeError("A sequence may be a binary mask. Binary mask alignment is not permitted")

            registration_method = sitk.ImageRegistrationMethod()

            # Similarity metric
            registration_method.SetMetricAsMattesMutualInformation(numberOfHistogramBins=50)

            # Type of transformation (rigid, affine, etc.)
            registration_method.SetInterpolator(sitk.sitkLinear)
            registration_method.SetOptimizerAsGradientDescent(learningRate=1.0, numberOfIterations=100,
                                                            convergenceMinimumValue=1e-6, convergenceWindowSize=10)
            registration_method.SetOptimizerScalesFromPhysicalShift()

            # Initial transformation guess (can be identity, affine, etc.)
            transform = sitk.CenteredTransformInitializer(reference_image_float, moving_image_float,
                                                        sitk.Euler3DTransform(),
                                                        sitk.CenteredTransformInitializerFilter.GEOMETRY)
            registration_method.SetInitialTransform(transform)

            # Execute the registration
            self.final_transform = registration_method.Execute(reference_image_float, moving_image_float)

            # Optional: apply the final transformation to the moving image
            self.transformed_image = sitk.Resample(moving_image_float, reference_image_float, self.final_transform,
                                                sitk.sitkLinear, 0.0, self.moving_image.GetPixelID())

            self.assert_correctness()

        except AssertionError:
            self.issues.append("Failed to properly register the images.")
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
            assert self.transformed_image.GetSize() == self.moving_image.GetSize()
            assert self.transformed_image.GetSpacing() == self.moving_image.GetSpacing() 
        except AssertionError:
            raise AssertionError("There is a change in the spacing or size of the transformed image")