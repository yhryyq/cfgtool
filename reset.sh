mv log_* traverselog/
rm -rf outdir_*_pyc
ps aux | grep 'dot2graph.*\.py' | grep -v grep | awk '{print $2}' | xargs kill -9
