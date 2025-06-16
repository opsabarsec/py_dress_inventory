"""
This script is the main entry point for the clothing inventory application.
It loads data from each subfolder in the folder "data" and generates a
dataframe with columns: folder_name, cloth_description.
"""

import pandas as pd
import os
from pathlib import Path
import sys
import openai

import ai_image_reader as describer
import openai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Now you can access the variables as if they were set normally
openai_api_key = os.getenv("OPENAI_API_KEY")
print("OpenAI API Key loaded:", openai_api_key is not None)


def find_subfolders(data_folder: str = "data") -> list:
    """Main function to build and display the inventory dataframe."""

    data_path = Path(data_folder)
    print(f"Looking for subfolders in: {data_path}")
    if data_path.exists():
        list_subfolders = [f.name for f in data_path.iterdir() if f.is_dir()]
        print("Subfolders in 'data':", list_subfolders)
        return list_subfolders
    else:
        print("Data folder does not exist.")
        return []


def build_description(subfolder):
    """Builds a description for the clothing items in the subfolder."""

    folder_path = Path("data") / subfolder
    print(f"Processing folder: {folder_path}")
    if not folder_path.exists():
        print(f"Folder '{folder_path}' does not exist.")
        return None
    # Get image files from the folder
    image_files = describer.get_image_files(str(folder_path))

    if not image_files:
        print(f"No image files found in '{folder_path}'.")
        return None

    # Describe clothing images using OpenAI client
    client = openai.OpenAI(api_key=openai_api_key)
    # Check if a description file already exists, in such a case we don't spend
    # money and time building a description again.
    description_file = folder_path / "description.txt"
    if description_file.exists():
        with open(description_file, "r", encoding="utf-8") as f:
            description = f.read().strip()
        print(f"Loaded description from '{description_file}'.")

    else:
        print(f"No description file found in '{subfolder}'. Generating description...")
        # Generate description using the describer
        description = describer.describe_clothing_images(client, image_files)
        # Save the description to a the generate.txt file in the subfolder
        with open(description_file, "w", encoding="utf-8") as f:
            f.write(description)
        print(f"Description for '{subfolder}': {description}")
    return description


def build_dataframe() -> pd.DataFrame:
    """Builds a DataFrame with folder names and their descriptions."""
    # List folders in the current directory. Simple check that we have the data folder
    current_dir_folders = [f.name for f in Path(".").iterdir() if f.is_dir()]
    print("Folders in current directory:", current_dir_folders)
    # get the list of subfolders in the "data" directory
    # each subfolder should contain images of clothing items

    list_subfolders = find_subfolders("data")
    print(f"Found {len(list_subfolders)} subfolders.")

    list_descriptions = []
    for subfolder in list_subfolders:
        description = build_description(subfolder)
        if description:
            list_descriptions.append(description)

    dict_descriptions = zip(list_subfolders, list_descriptions)

    df = pd.DataFrame(dict_descriptions, columns=["folder_name", "cloth_description"])
    df.to_csv("clothing_inventory.csv", index=False)

    return df


if __name__ == "__main__":
    # Build the DataFrame with clothing descriptions
    df = build_dataframe()
    print("Created the inventory with clothing descriptions:")
    print("please check the clothing_inventory.csv file.")
