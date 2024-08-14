

start_line=1
end_line=40

file_name="javac_200_commits.csv" #pyc_inter_bug_commits_81+.csv casestudy.csv casestudy_2.csv pyc_inter_bug_commits_wen.csv pyc_inter_bug_commits_temp.csv

shas=($(awk -F, -v start=$start_line -v end=$end_line 'NR>=start && NR<=end {print $1}' $file_name))
projects=($(awk -F, -v start=$start_line -v end=$end_line 'NR>=start && NR<=end {print $2}' $file_name))

for ((i = 0; i < ${#shas[@]}; i++)); do
	sha=${shas[i]}
        project=${projects[i]}
	#sha="535989ecb68da1affc531e866d190bfdbd9fc5fc"
	#project="python/cpython"
	
	#repo=$(echo $project | cut -d'/' -f2)
	repo="$(echo $project | cut -d'/' -f2)_$sha"
	git clone https://github.com/${project}.git $repo
	#git clone https://github.com/${project}.git
	
	cd $repo
	git fetch origin $sha
	git reset --hard $sha
	git log -2 --pretty=format:"%H"
	bug_sha=$(git log -2 --pretty=format:"%H" | sed -n '2p')
	git fetch origin $bug_sha
	git reset --hard $bug_sha

	cd ..
	python3 split_c_java.py ./$repo

	mkdir outdir_$(echo $project | cut -d'/' -f2)_${sha}_javac

	echo ========parse the c code in $repo========
	base_dir="./c_$repo"
	# 需要将文件夹名代表得包名赋值到所有dot文件上
	time(
	for folder in "$base_dir"/*/; do
	    if [ -d "$folder" ]; then
		./joern-parse $folder
		./joern-export --repr cfg --out outdir_temp
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

	echo ========parse the java code in $repo========
	base_dir="./java_$repo"
	time(
	for folder in "$base_dir"/*/; do
	    if [ -d "$folder" ]; then
		./joern-parse $folder
		./joern-export --repr cfg --out outdir_temp
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

	rm -rf c_$repo
	rm -rf java_$repo
	#rm -rf $repo
done
