#shas=("a13a7b82d4664c767575097c4a60c0b5fcd1098a" "9fede9489d98707240d0e7213104bc617daa4c75" "c320f7e296651cb624857ec6d88df8fc10fd0bb1" "60dc9730d5652f0632cd43caef437f01a734e374" "8fa4b7364d98659dd8fe28727f60d99a14b95850")
#projects=("scipy/scipy" "scipy/scipy" "scipy/scipy" "scipy/scipy" "scipy/scipy")

start_line=11
end_line=20

file_name="casestudy_2.csv"

shas=($(awk -F, -v start=$start_line -v end=$end_line 'NR>=start && NR<=end {print $1}' $file_name))
projects=($(awk -F, -v start=$start_line -v end=$end_line 'NR>=start && NR<=end {print $2}' $file_name))

for ((i = 0; i < ${#shas[@]}; i++)); do
	sha=${shas[i]}
        project=${projects[i]}
	#sha="535989ecb68da1affc531e866d190bfdbd9fc5fc"
	#project="python/cpython"
	repo=$(echo $project | cut -d'/' -f2)

	git clone https://github.com/${project}.git
	cd $repo
	git fetch origin $sha
	git reset --hard $sha
	git log -2 --pretty=format:"%H"
	bug_sha=$(git log -2 --pretty=format:"%H" | sed -n '2p')
	git fetch origin $bug_sha
	git reset --hard $bug_sha

	cd ..
	python3 split_c_py.py ./$repo

	mkdir outdir_${repo}_${sha}_pyc

	echo ========parse the c code in $repo========
	base_dir="./c_$repo"
	time(
	for folder in "$base_dir"/*/; do
	    if [ -d "$folder" ]; then
		./joern-parse $folder
		./joern-export --repr cfg --out outdir_temp
		src_folder="outdir_temp"
		dest_folder="outdir_${repo}_${sha}_pyc"
		for file in "$src_folder"/*; do
		    folder_name=$(basename "$folder")
		    filename=$(basename "$file")
		    cp "$file" "$dest_folder/c_${folder_name}_${filename}"
		done
		rm -rf outdir_temp
	    fi
	done
	)

	echo ========parse the py code in $repo========
	base_dir="./py_$repo"
	time(
	for folder in "$base_dir"/*/; do
	    if [ -d "$folder" ]; then
		./joern-parse $folder
		./joern-export --repr cfg --out outdir_temp
		src_folder="outdir_temp"
		dest_folder="outdir_${repo}_${sha}_pyc"
		for file in "$src_folder"/*; do
		    folder_name=$(basename "$folder")
		    filename=$(basename "$file")
		    cp "$file" "$dest_folder/py_${folder_name}_${filename}"
		done
		rm -rf outdir_temp
	    fi
	done
	)

	rm -rf c_$repo
	rm -rf py_$repo
	rm -rf $repo
done
