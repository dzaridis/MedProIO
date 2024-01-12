
# MedProIO package

A package to perform specific Medical Image processing operations based on SimpleITK such as alignment, resapling, and volume cropping\padding


## Installation

Install MedProIO via pip

```bash
pip install MedProIO
```
    
## Usage/Examples

### Sequences Alignment
```python
from MedProIO import Alignment
res = Alignment.AlignmentRegistration()

# set the reference Sitk object 
res.set_reference_image(T2)

# set the moving Sitk object 
res.set_moving_image(ADC)

# execute
res.execute_processing()

# get the transformed moving object
tr = res.get_transformed_image()

# Get a list with potential issues arose
issues = res.get_issues()
```

### Resampling to Spacing
```python
from MedProIO import Resampler
res = Resampler.ResamplerToSpacing()

# set the reference Sitk object 
res.set_reference_image(T2)

# set the spacing 
res.set_spacing(spacing=(0.5, 0.5, 3.0))

# execute
res.execute_processing()

# get the transformed moving object
tr = res.get_transformed_image()

# Get a list with potential issues arose
issues = res.get_issues()
```

### Resampling between Sequences
```python
from MedProIO import Coregistrator
res = Coregistrator.SequenceResampler()

# set the reference Sitk object 
res.set_reference_image(T2)

# set the moving Sitk object 
res.set_moving_image(ADC)

# execute
res.execute_processing()

# get the transformed moving object
tr = res.get_transformed_image()

# Get a list with potential issues arose
issues = res.get_issues()
```

### Volume Crop or Padding to dimensions
```python
from MedProIO import CropAndPad
res = CropAndPad.VolumeCropperAndPadder()

# set the reference Sitk object 
res.set_reference_image(T2)

# set the target size
res.set_target_size(target_size=(256,256,24))

# execute
res.execute_processing()

# get the transformed moving object
tr = res.get_transformed_image()

# Get a list with potential issues arose
issues = res.get_issues()
```


## Authors

- [Dimitrios Zaridis](dimzaridis@gmail.com)


## Badges

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)

![Python](https://img.shields.io/badge/Python-3.8-green)
