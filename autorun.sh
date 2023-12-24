sha=$1
project=$2
func=$3
line=$4
borf=$5

bash downloadsha.sh $sha $project

repo="$(echo $project | cut -d'/' -f2)_$sha"

python3 dot2graph.py "./outdir_${repo}_pyc" "./$repo" $func $line $borf 1>"${sha}_${borf}_log" 2>&1 & 