#!/bin/bash
# 参数1：输入项目所在文件夹
# 参数2：输入dot文件所在文件夹
# 参数3：c文件所在文件夹
proj_dir=$1 # 输入相对地址
dot_dir=$2
c_dir=$3
imports_dir=$4
if [ -z "$JOERN_DIR_PATH" ]; then
  echo "Please set JOERN_DIR_PATH to process further"
  exit  
fi


if [ -z "$1" ]; then
  echo "Please input your proj_dir"
  exit
else
  echo "Processing"
fi

python ./split_java_c.py $1
./testtool.sh $1
# python ./dot2graph_javac.py $2 $3 $4