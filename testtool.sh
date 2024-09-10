#!/bin/bash
# 首先运行split分块，然后运行testtool.sh提取import、dot等信息，最后运行dot2graph_javac.py
project=$(basename "$1")
repo="java_"$project
sha="123"
dest_folder="outdir_$(echo $project | cut -d'/' -f2)_${sha}_javac"
echo ========parse the java code in $repo========
base_dir=$repo
mkdir "outdir_$(echo $project | cut -d'/' -f2)_${sha}_javac"
mkdir "imports_data"
# 需要将文件夹名代表得包名赋值到所有dot文件上
time(
for file in "$base_dir"/*; do
	echo $file
    if [ -f "$file" ]; then
	/home/kali/桌面/joern-cli/joern-parse $file
	# 读取imports信息
	/home/kali/桌面/joern-cli/joern --script getimport.sc --param outFile="./imports_data/$(basename "$file").pkl" --param cpgFile="./cpg.bin"
	# 使用diy提取dot文件
	echo $dest_folder
	/home/kali/桌面/joern-cli/joern --script exportdot.sc --param outFile="$dest_folder" --param language="java" --param cpgFile="./cpg.bin"
	# /home/kali/桌面/joern-cli/joern-export --repr cpg14 --out outdir_temp
	# src_folder="outdir_temp"
	
	# for file in "$src_folder"/*; do
	#     folder_name=$(basename "$file")
	#     filename=$(basename "$file")
	#     cp "$file" "$dest_folder/java_${folder_name}_${filename}"
	# done
	rm -rf outdir_temp
    fi
done
)

repo="c_"$project
echo ========parse the c code in $repo========
base_dir=$repo
time(
for file in "$base_dir"/*; do
    if [ -f "$file" ]; then
	/home/kali/桌面/joern-cli/joern-parse $file
	# /home/kali/桌面/joern-cli/joern-export --repr cpg14 --out outdir_temp

	# src_folder="outdir_temp"
	/home/kali/桌面/joern-cli/joern --script exportdot.sc --param outFile="$dest_folder" --param language="c" --param cpgFile="./cpg.bin"
	# for file in "$src_folder"/*; do
	#     folder_name=$(basename "$file")
	#     filename=$(basename "$file")
	#     cp "$file" "$dest_folder/c_${folder_name}_${filename}"
	# done
	rm -rf outdir_temp
    fi
done
)
rm cpg.bin
rm -rf workspace

python ./fixname.py $dest_folder


