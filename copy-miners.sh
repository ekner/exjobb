while read p; do
  cp "/home/gustav/kod/dataset/filtered/$p.wasm" "/home/gustav/kod/dataset/non-miners-213/" 
done < /home/gustav/kod/dataset/non-miners-list-213.txt
