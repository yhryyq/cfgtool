import os
import shutil
import sys

# 优先使用该脚本对不同文件的名字进行修改
def organize_files_by_extension(path):
    # Extract folder name from the path
    folder = os.path.basename(path)

    # Create directories for c and python files if they don't exist
    c_folder = f"c_{folder}"
    java_folder = f"java_{folder}"

    if not os.path.exists(c_folder):
        os.makedirs(c_folder)
    if not os.path.exists(java_folder):
        os.makedirs(java_folder)

    # Recursively walk through the directory
    for root, dirs, files in os.walk(path):
        for file in files:
            # print(os.path.dirname(path))
            # Check the file extension and set the target folder
            if file.endswith('.c'):
                target_folder = os.path.join(c_folder, file.rsplit('.', 1)[0])
            elif file.endswith('.java'):
                # target_folder = os.path.join(java_folder, file.rsplit('.', 1)[0])
                with open(root + '/' + file, 'r') as f:
                    try:
                        while True:
                            first_line = next(f)
                            if first_line.startswith("package"):
                                break
                            # 如果不存在package，那么直接用相对地址
                        target_folder = first_line[8:first_line.find(";")].replace('.', '-')
                    except StopIteration:
                        target_folder = root[len(path) + 1:]
                target_folder = os.path.join(java_folder, target_folder + "-" + file.rsplit('.', 1)[0])
            else:
                continue  # Skip files with other extensions

            # Create the target folder if it doesn't exist
            if not os.path.exists(target_folder):
                os.makedirs(target_folder)

            # Move the file to the target folder
            shutil.move(os.path.join(root, file), os.path.join(target_folder, file))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 split_c_java.py <path>")
        sys.exit(1)

    path = sys.argv[1]
    organize_files_by_extension(path)

