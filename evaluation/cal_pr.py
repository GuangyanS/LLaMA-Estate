import os
import json
from collections import defaultdict
from sklearn.metrics import precision_score, recall_score
from tqdm import tqdm

# Define the paths to the prediction and ground truth folders
pred_folder = '/home/dxleec/gysun/datasets/estate/202403010927_pred_td/'
true_folder = '/home/dxleec/gysun/datasets/estate/202403010927_json/'

# List the filenames in each folder
pred_files = set(os.listdir(pred_folder))
true_files = set(os.listdir(true_folder))

# Find the intersection to ensure we only match files present in both folders
common_files = pred_files.intersection(true_files)

# Initialize the storage for each key's true and predicted values
precision = defaultdict(list)
recall = defaultdict(list)

# Process the files with tqdm for progress display
for filename in tqdm(common_files, desc="Processing files"):
    try:
        # Load the prediction JSON file
        with open(os.path.join(pred_folder, filename), 'r') as f:
            pred_data = json.load(f)

        # Load the ground truth JSON file
        with open(os.path.join(true_folder, filename), 'r') as f:
            true_data = json.load(f)
    except json.JSONDecodeError:
        # Print the name of any file that has an incorrect JSON format and skip processing
        print(f"Skipping file with incorrect JSON format: {filename}")
        continue

    # Assume the JSON structure is consistent across files
    for key in pred_data:
        if key in true_data:
            is_exist = pred_data[key] is not None
            recall[key].append(is_exist)

            if is_exist is False:
                continue
            
            true_value = true_data[key]
            pred_value = pred_data[key]
            
            if isinstance(pred_value, str):
                true_value = true_value.lower()
                pred_value = pred_value.lower()

            # Check if the prediction is correct
            precision[key].append(true_value == pred_value)
            
            

# Calculate precision and recall for each key
for key in recall:
    score = sum(recall[key]) / len(recall[key])
    print(f"Key: {key} - Recall: {score}")
    
for key in precision:
    scpre = sum(precision[key]) / len(precision[key])
    print(f"Key: {key} - Precision: {score}") 
