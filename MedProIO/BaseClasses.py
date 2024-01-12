from abc import ABC, abstractmethod

import SimpleITK as sitk
import numpy as np

class BaseImageRegistration(ABC):
    """
    Abstract base class for medical image registration operations.
    This class provides the basic framework for image registration and can be extended for various image processing tasks.
    """

    def __init__(self):
        """
        Initialize the BaseImageRegistration object.
        """
        self.reference_image = None
        self.moving_image = None
        self.transformed_image = None
        self.issues = []

    @abstractmethod
    def execute_processing(self):
        """
        Abstract method to resample images. Must be implemented by subclasses.
        """
        pass

    @abstractmethod
    def assert_correctness(self):
        """
        Abstract method to assert the correctness of the registration. Must be implemented by subclasses.
        """
        pass

    def set_reference_image(self, image):
        """
        Set the reference image.

        :param image: A SimpleITK image to be set as the reference image.
        """
        if not isinstance(image, sitk.Image):
            raise TypeError("The reference image must be a SimpleITK Image object.")
        self.reference_image = image

    def set_moving_image(self, image):
        """
        Set the moving image.

        :param image: A SimpleITK image to be set as the moving image.
        """
        if not isinstance(image, sitk.Image):
            raise TypeError("The moving image must be a SimpleITK Image object.")
        self.moving_image = image

    def get_transformed_image(self):
        """
        Get the transformed (registered) image.

        :return: A SimpleITK image that is the result of the registration process.
        """
        return self.transformed_image
    
    def get_issues(self):
        """
        Get the transformed (registered) image.

        :return: A SimpleITK image that is the result of the registration process.
        """
        return self.issues