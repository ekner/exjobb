while read p; do
  cp "/home/gustav/kod/dataset/filtered/$p.wasm" "/home/gustav/kod/dataset/filtered-miners/" 
done < /home/gustav/kod/dataset/miners-list.txt
