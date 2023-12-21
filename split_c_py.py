import os
import shutil
import sys

def organize_files_by_extension(path):
    # Extract folder name from the path
    folder = os.path.basename(path)

    # Create directories for c and python files if they don't exist
    c_folder = f"c_{folder}"
    py_folder = f"py_{folder}"

    if not os.path.exists(c_folder):
        os.makedirs(c_folder)
    if not os.path.exists(py_folder):
        os.makedirs(py_folder)

    # Recursively walk through the directory
    for root, dirs, files in os.walk(path):
        for file in files:
            # Check the file extension and set the target folder
            if file.endswith('.c'):
                target_folder = os.path.join(c_folder, file.rsplit('.', 1)[0])
            elif file.endswith('.py'):
                target_folder = os.path.join(py_folder, file.rsplit('.', 1)[0])
            else:
                continue  # Skip files with other extensions

            # Create the target folder if it doesn't exist
            if not os.path.exists(target_folder):
                os.makedirs(target_folder)

            # Move the file to the target folder
            shutil.move(os.path.join(root, file), os.path.join(target_folder, file))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 split_c_py.py <path>")
        sys.exit(1)

    path = sys.argv[1]
    organize_files_by_extension(path)

