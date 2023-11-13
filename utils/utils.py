# utils/utils.py
import json
import os

def read_json(file_path):
    if not os.path.exists(file_path):
        return None  # Or handle the error as needed
    with open(file_path, 'r') as file:
        return json.load(file)
