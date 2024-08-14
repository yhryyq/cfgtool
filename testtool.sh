#!/bin/bash
# 首先运行split分块，然后运行testtool.sh提取import、dot等信息，最后运行dot2graph_javac.py
repo="java_test"
project="test"
sha="123"
echo ========parse the java code in $repo========
base_dir=$repo
mkdir "outdir_$(echo $project | cut -d'/' -f2)_${sha}_javac"
mkdir "imports_data"
# 需要将文件夹名代表得包名赋值到所有dot文件上
time(
for folder in "$base_dir"/*/; do
    if [ -d "$folder" ]; then
	/home/kali/桌面/joern-cli/joern-parse $folder
	# 读取imports信息
	/home/kali/桌面/joern-cli/joern --script getimport.sc --param outFile="./imports_data/$(basename "$folder").pkl"
	/home/kali/桌面/joern-cli/joern-export --repr cpg14 --out outdir_temp
	src_folder="outdir_temp"
	dest_folder="outdir_$(echo $project | cut -d'/' -f2)_${sha}_javac"
	for file in "$src_folder"/*; do
	    folder_name=$(basename "$folder")
	    filename=$(basename "$file")
	    cp "$file" "$dest_folder/java_${folder_name}_${filename}"
	done
	rm -rf outdir_temp
    fi
done
)

repo="c_test"
echo ========parse the java code in $repo========
base_dir=$repo
time(
for folder in "$base_dir"/*/; do
    if [ -d "$folder" ]; then
	/home/kali/桌面/joern-cli/joern-parse $folder
	/home/kali/桌面/joern-cli/joern-export --repr cpg14 --out outdir_temp

	src_folder="outdir_temp"
	dest_folder="outdir_$(echo $project | cut -d'/' -f2)_${sha}_javac"
	for file in "$src_folder"/*; do
	    folder_name=$(basename "$folder")
	    filename=$(basename "$file")
	    cp "$file" "$dest_folder/c_${folder_name}_${filename}"
	done
	rm -rf outdir_temp
    fi
done
)
rm -rf workspace