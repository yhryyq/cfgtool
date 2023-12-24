#shas=("a13a7b82d4664c767575097c4a60c0b5fcd1098a" "9fede9489d98707240d0e7213104bc617daa4c75" "c320f7e296651cb624857ec6d88df8fc10fd0bb1" "60dc9730d5652f0632cd43caef437f01a734e374" "8fa4b7364d98659dd8fe28727f60d99a14b95850")


#sha="04ab04d93d4d7a4d241fe0ceb725436a8b6c8c2e"
#project="numpy/numpy"

sha=$1
project=$2

repo="$(echo $project | cut -d'/' -f2)_$sha"
git clone https://github.com/${project}.git $repo
cd $repo
git fetch origin $sha
git reset --hard $sha
git log -2 --pretty=format:"%H"
bug_sha=$(git log -2 --pretty=format:"%H" | sed -n '2p')
git fetch origin $bug_sha
git reset --hard $bug_sha


