#!/bin/bash
start_line=141
end_line=160

file_name="pyc_200_commits.csv" #pyc_inter_bug_commits_81+.csv casestudy.csv casestudy_2.csv pyc_inter_bug_commits_wen.csv pyc_inter_bug_commits_temp.csv

shas=($(awk -F, -v start=$start_line -v end=$end_line 'NR>=start && NR<=end {print $1}' $file_name))
projects=($(awk -F, -v start=$start_line -v end=$end_line 'NR>=start && NR<=end {print $2}' $file_name))

echo $shas
echo $projects