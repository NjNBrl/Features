import os
from pathlib import Path

def combine_txt_files(folder1, folder2, output_folder):
    """
    Combines matching txt files from two folders.
    - Files in folder1 are named like `abc_combined.txt`
    - Files in folder2 are named like `abc.txt`
    - Combines them only if names match before `_combined`
    - Output contains folder1 content first, then folder2
    """

    folder1 = Path(folder1)
    folder2 = Path(folder2)
    output_folder = Path(output_folder)
    output_folder.mkdir(exist_ok=True)

    for file1 in folder1.glob("*.txt"):
        if "_combined" not in file1.stem:
            continue

        base_name = file1.stem.replace("_combined", "")
        file2 = folder2 / f"{base_name}.txt"

        if file2.exists():
            output_file = output_folder / f"{base_name}_merged.txt"

            with open(file1, "r") as f1, open(file2, "r") as f2, open(output_file, "w") as fout:
                fout.write(f1.read().strip() + "\n")
                fout.write(f2.read().strip() + "\n")

            print(f"✅ Combined: {file1.name} + {file2.name} → {output_file.name}")
        else:
            print(f"⚠️ No match found for {file1.name}")

if __name__ == "__main__":
    combine_txt_files("6A.emotin_labelled_caption", "7.REMI", "8.FINAL DATA")
