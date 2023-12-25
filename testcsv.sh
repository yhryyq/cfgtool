start_line=72
end_line=81
file_name="casestudy.csv"


shas=($(awk -F, -v start=$start_line -v end=$end_line 'NR>=start && NR<=end {print $1}' $file_name))
projects=($(awk -F, -v start=$start_line -v end=$end_line 'NR>=start && NR<=end {print $2}' $file_name))

# 输出数组内容进行检查
echo "SHAs:"
for sha in "${shas[@]}"; do
    echo "$sha"
done

echo "Projects:"
for project in "${projects[@]}"; do
    echo "$project"
done
