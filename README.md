# NuCLS Dataset Organization

This repository contains scripts and instructions for organizing the NuCLS dataset, a large-scale collection for nucleus classification, localization, and segmentation in breast cancer images.

## Overview

The NuCLS dataset contains over **220,000 labeled nuclei** from breast cancer images sourced from TCGA. Annotations were created through a collaborative effort among pathologists, pathology residents, and medical students using the Digital Slide Archive.

This dataset is ideal for:
- Nuclear detection
- Classification
- Segmentation
- Interrater analysis

## Dataset Details

**Source:** [NuCLS Website](https://sites.google.com/view/nucls/home)

### Structure of the Original Dataset

Each dataset folder includes four sub-folders:
- **rgb:** FOV images (`.png`)
- **csv:** Annotation coordinates (`.csv`)
- **mask:** Mask images (`.png`)
- **visualization:** Visualization images (`.png`)

**Image Resolution:** All images are at 0.2 microns-per-pixel.  
**Coordinate Units:** Pixel units at 0.2 microns-per-pixel.

### CSV Annotation File

Each CSV file includes:
- `raw_classification`: Raw cell type (13 total)
- `main_classification`: Nucleus class (7 total)
- `super_classification`: Nucleus superclass (4 total)
- `type`: Annotation type (`rectangle` or `polyline`)
- `xmin`, `ymin`, `xmax`, `ymax`: Bounding box coordinates
- `coords_x`, `coords_y`: Comma-separated polygon boundary coordinates

### Mask Format

- **First channel:** Encodes class labels.
- **Second and third channels:** Their product provides the unique instance label.
- **FOV area:** Represented in gray and included in the class table.

**Note:** Unlike the CSV files, the mask images do not differentiate between bounding boxes and segmentations.

## Data Organization Process

In this repository, the dataset has been reorganized as follows:

1. **Selection:**
   - **Dataset type:** Corrected single-rater dataset.
   - **Split:** Used folder-1 for train and test split (RGB, annotation, and mask).

2. **Organization:**
   - **Train, Test, and Validation:** Integrated into a single folder to allow flexible splitting during experiments.
   - **Sub-categories:** Organized based on cell types into:
     - **Object Detection:** Uses rectangular annotations (bounding boxes).  
       *Note: Masks are removed as they are not required for object detection.*
     - **Semantic Segmentation:** Uses polygon annotations (polylines) with corresponding masks.

3. **Additional Notes:**
   - Rectangular masks in some cases output entirely white images. Therefore, two separate datasets (rectangular and polyline) were created to serve object detection and semantic segmentation tasks respectively.
   - A `README.txt` is generated in the output folder summarizing the number of images per tissue type for each task.

## Repository Structure

