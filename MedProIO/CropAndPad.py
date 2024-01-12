import SimpleITK as sitk
import numpy as np
from MedProIO import BaseClasses

class VolumeCropperAndPadder(BaseClasses.BaseImageRegistration):
    """
    A class that extends BaseImageRegistration for volume cropping and padding.
    This class handles the center cropping and/or padding of a SimpleITK volume to a target size.
    """

    def __init__(self):
        super().__init__()
        self.issues = []  # To keep track of any issues encountered
        self.target_size = (256, 256, 24)

    def execute_processing(self):
        """
        Executes the center cropping and padding of the moving image to the target size.
        The target size should be set before calling this method.
        """
        try:
            self.transformed_image = self.__center_crop_and_pad_sitk_volume(self.reference_image, self.target_size)
            self.assert_correctness()
        except AssertionError:
            self.issues.append("Failed to produce the desired target size")
        except Exception as e:
            self.issues.append(f"Unexpected error: {e}")
    
    def set_target_size(self, target_size:np.ndarray):
        self.target_size = target_size
    
    def assert_correctness(self):
        """
        Asserts the correctness of the resampling by checking the metadata.
        """
        try:
            assert self.transformed_image.GetSize() == self.target_size
        except AssertionError:
            raise AssertionError("Reference and Moving SimpleITK images do not have matching metadata after the registration.")

    @staticmethod
    def __center_crop_and_pad_sitk_volume(volume, target_size):
        """
        Center crops and/or pads a 3D SimpleITK volume to a given target size.
        
        :param volume: The input SimpleITK image (volume).
        :param target_size: A tuple or list of three integers (depth, width, height).
        :return: The center cropped and/or padded SimpleITK image.
        """
        # Get the size of the current volume
        current_size = volume.GetSize()
        
        # Calculate the difference between current size and target size
        size_diff = [t - c for t, c in zip(target_size, current_size)]
        
        # Calculate the padding for each dimension
        # If the size difference is negative, we need to crop, so set padding to zero
        # If the size difference is positive, we need to pad
        pad_before = [max(0, d // 2) for d in size_diff]
        pad_after = [max(0, d - pb) for d, pb in zip(size_diff, pad_before)]
        
        # Pad the volume if necessary
        if any(size_diff[dim] > 0 for dim in range(3)):
            volume = sitk.ConstantPad(volume, pad_before, pad_after, constant=0)
        
        # Update current size after padding
        current_size = volume.GetSize()
        
        # Calculate the region to crop
        start_idx = [int((c - t) / 2) for c, t in zip(current_size, target_size)]
        start_idx = [max(0, min(current_size[i] - target_size[i], start_idx[i])) for i in range(3)]
        # Use the RegionOfInterest filter to extract the crop
        roi_filter = sitk.RegionOfInterestImageFilter()
        roi_filter.SetSize(target_size)
        roi_filter.SetIndex(start_idx)
        
        cropped_volume = roi_filter.Execute(volume)
        
        return cropped_volume