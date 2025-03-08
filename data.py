import os
import shutil
import pandas as pd
csv_file = r"C:\Users\ADMIN\Desktop\NuCLS\fold_1_test.csv"
rgb_folder = r"C:\Users\ADMIN\Desktop\NuCLS\rgb\rgb"
renamed_rgb_folder = r"C:\Users\ADMIN\Desktop\NuCLS\data\test\rgb"
data = pd.read_csv(csv_file)
if not os.path.exists(renamed_rgb_folder):
    os.makedirs(renamed_rgb_folder)
for index, row in data.iterrows():
    image_name_csv = row['slide_name']
    for filename in os.listdir(rgb_folder):
        image_name_rgb = filename.split("_id")[0]
        if image_name_csv == image_name_rgb:
            source_path = os.path.join(rgb_folder, filename)
            destination_path = os.path.join(renamed_rgb_folder, image_name_csv + '.png')
            shutil.move(source_path, destination_path)
            print(f'Renamed and moved {filename} to the renamed RGB folder as {image_name_csv}.png')
            
    else:
        print(f'Image {image_name_csv} not found in the RGB folder.')

print('Image renaming and moving completed.')




        

