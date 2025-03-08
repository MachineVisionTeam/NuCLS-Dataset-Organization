import os
from collections import defaultdict
import pandas as pd
import numpy as np
from PIL import Image, ImageDraw
from tqdm import tqdm

def organize_nucls_data(image_dir, mask_dir, annotation_dir, output_dir):
    """
    Organizes the NuCLS dataset into:
    - Object Detection: Cropped images (no masks) for rectangular annotations.
    - Semantic Segmentation: Cropped images and masks for polygon annotations.
    Generates a README.txt with counts per cell type and task.
    """
    # Define cell types
    cell_types = {
        "fibroblast": "fibroblast",
        "plasma_cell": "plasma_cell",
        "tumor": "tumor",
        "lymphocyte": "lymphocyte",
        "macrophage": "macrophage",
        "mitotic_figure": "mitotic_figure",
        "vascular_endothelium": "vascular_endothelium",
        "myoepithelium": "myoepithelium",
        "apoptotic_body": "apoptotic_body",
        "neutrophil": "neutrophil",
        "ductal_epithelium": "ductal_epithelium",
        "eosinophil": "eosinophil",
        "unlabeled": "unlabeled"
    }

    # Initialize counts
    counts = defaultdict(lambda: defaultdict(int))

    # Create base output directories
    os.makedirs(os.path.join(output_dir, "object_detection"), exist_ok=True)
    os.makedirs(os.path.join(output_dir, "semantic_segmentation"), exist_ok=True)

    # Get all image files
    image_files = [f for f in os.listdir(image_dir) if f.endswith('.png')]
    print(f"Found {len(image_files)} images.")

    # Process each image
    for image_file in tqdm(image_files, desc="Processing images"):
        image_name = os.path.splitext(image_file)[0]
        annotation_file = os.path.join(annotation_dir, f"{image_name}.csv")
        mask_file = os.path.join(mask_dir, f"{image_name}.png")  # Mask filename matches image name

        # Skip if any file is missing
        if not os.path.exists(os.path.join(image_dir, image_file)):
            print(f"Missing image: {image_file}. Skipping...")
            continue
        if not os.path.exists(mask_file):
            print(f"Missing mask: {mask_file}. Skipping...")
            continue
        if not os.path.exists(annotation_file):
            print(f"Missing annotation: {annotation_file}. Skipping...")
            continue

        # Load data
        image = np.array(Image.open(os.path.join(image_dir, image_file)))
        mask = np.array(Image.open(mask_file))
        annotations = pd.read_csv(annotation_file)

        # Ensure mask and image dimensions match
        if mask.shape[:2] != image.shape[:2]:
            print(f"Resizing mask for {image_name} to match image dimensions.")
            mask = np.array(Image.fromarray(mask).resize((image.shape[1], image.shape[0]), Image.NEAREST))

        # Process annotations
        for idx, row in annotations.iterrows():
            cell_type = row['raw_classification']
            if cell_type not in cell_types:
                print(f"Unknown cell type: {cell_type}. Skipping...")
                continue

            # Process rectangular annotations (object detection)
            if row['type'] == 'rectangle':
                xmin = max(0, int(row['xmin']))
                ymin = max(0, int(row['ymin']))
                xmax = min(mask.shape[1]-1, int(row['xmax']))
                ymax = min(mask.shape[0]-1, int(row['ymax']))

                # Crop image
                cropped_image = image[ymin:ymax, xmin:xmax]

                # Save to object detection folder
                obj_dir = os.path.join(output_dir, "object_detection", cell_type, "images")
                os.makedirs(obj_dir, exist_ok=True)
                image_filename = os.path.join(obj_dir, f"image_{image_name}_{idx}.png")
                Image.fromarray(cropped_image).save(image_filename)
                counts["object_detection"][cell_type] += 1

            # Process polyline annotations (semantic segmentation)
            elif row['type'] == 'polyline':
                coords_x = list(map(int, row['coords_x'].split(',')))
                coords_y = list(map(int, row['coords_y'].split(',')))

                # Clamp coordinates to image dimensions
                coords_x = [max(0, min(x, mask.shape[1]-1)) for x in coords_x]
                coords_y = [max(0, min(y, mask.shape[0]-1)) for y in coords_y]

                # Create polygon mask
                poly_mask = Image.new('L', (mask.shape[1], mask.shape[0]), 0)
                ImageDraw.Draw(poly_mask).polygon(list(zip(coords_x, coords_y)), outline=255, fill=255)
                instance_mask = np.array(poly_mask)

                # Crop image and mask to the polygon's bounding box
                rows = np.any(instance_mask, axis=1)
                cols = np.any(instance_mask, axis=0)
                if not np.any(rows) or not np.any(cols):
                    print(f"Empty mask for instance {idx} in {image_name}. Skipping...")
                    continue
                ymin, ymax = np.where(rows)[0][[0, -1]]
                xmin, xmax = np.where(cols)[0][[0, -1]]

                cropped_image = image[ymin:ymax, xmin:xmax]
                cropped_mask = instance_mask[ymin:ymax, xmin:xmax]

                # Save to semantic segmentation folder
                sem_dir_images = os.path.join(output_dir, "semantic_segmentation", cell_type, "images")
                sem_dir_masks = os.path.join(output_dir, "semantic_segmentation", cell_type, "masks")
                os.makedirs(sem_dir_images, exist_ok=True)
                os.makedirs(sem_dir_masks, exist_ok=True)
                
                image_filename = os.path.join(sem_dir_images, f"image_{image_name}_{idx}.png")
                mask_filename = os.path.join(sem_dir_masks, f"mask_{image_name}_{idx}.png")
                
                Image.fromarray(cropped_image).save(image_filename)
                Image.fromarray(cropped_mask).save(mask_filename)
                counts["semantic_segmentation"][cell_type] += 1

            else:
                print(f"Unknown annotation type: {row['type']}. Skipping...")
                continue

    # Generate README.txt with counts
    readme_path = os.path.join(output_dir, "README.txt")
    with open(readme_path, "w") as f:
        f.write("Dataset Summary\n")
        f.write("================\n\n")

        # Object Detection counts
        f.write("Object Detection (rectangular bounding boxes):\n")
        for cell_type, count in counts["object_detection"].items():
            f.write(f"- {cell_type}: {count} images\n")
        f.write("\n")

        # Semantic Segmentation counts
        f.write("Semantic Segmentation (polygon masks):\n")
        for cell_type, count in counts["semantic_segmentation"].items():
            f.write(f"- {cell_type}: {count} images\n")

    print("----------Finished organizing----------")
    print(f"README.txt saved to {output_dir}")

# Usage
image_dir = "/home/skoganti/sample/Sample/MaskRCNN/train_main/rgb"
mask_dir = "/home/skoganti/sample/Sample/MaskRCNN/train_main/mask"
annotation_dir = "/home/skoganti/sample/Sample/MaskRCNN/train_main/annotation"
output_dir = "/home/skoganti/sample/Sample/MaskRCNN/main_organised"

organize_nucls_data(image_dir, mask_dir, annotation_dir, output_dir)