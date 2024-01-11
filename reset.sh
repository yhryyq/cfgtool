
ps aux | grep 'dot2graph.*\.py' | grep -v grep | awk '{print $2}' | xargs kill -9
mv log_* traverselog/
rm -rf outdir_*_pyc
rm run.log

while IFS= read -r line; do
    rm -rf "$line"
done < temp_repo_name.txt

rm temp_repo_name.txt

