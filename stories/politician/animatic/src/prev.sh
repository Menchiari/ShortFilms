#!/bin/bash
# usage: prev.sh <outdir> <ids...>   preview 3 frames per shot in 3 workers
A=$(cd "$(dirname "$0")" && pwd)
cd $A; OUT=$1; shift; IDS=("$@"); N=${#IDS[@]}
for k in 0 1 2; do
  SEL=(); for ((i=k; i<N; i+=3)); do SEL+=("${IDS[$i]}"); done
  PREVIEW=1 timeout 3000 python run2.py $A/$OUT "${SEL[@]}" > log_${OUT}_$k.txt 2>&1 &
done
wait
grep -h "DONE\|Error\|Traceback" log_${OUT}_*.txt | sort | uniq -c | sort -rn | head -40
echo ALLDONE
