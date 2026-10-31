. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
export HOME=$FENRIS_HOME PSUSER=box; cd ~
say "我在哪？pwd = print working directory"
runp 'pwd'
say "這裡有什麼？ls 列出檔案"
runp 'ls'
say "加 -la：顯示隱藏檔（點開頭）和詳細資訊"
runp 'ls -la' 2.5
say "cd 走進資料夾，tree 看整棵樹"
runp 'cd fenris_ws/src/guide_dog'
runp 'tree' 2.5
say "cat 把檔案印出來"
runp 'cat config/params.yaml' 2.2
say "cd .. 回上一層；cd ~ 回家"
runp 'cd ..'
runp 'cd ~'
say "find：整個家目錄找 yaml 檔"
runp 'find . -name "*.yaml"' 2.2
say "grep -r：所有檔案裡搜尋 key 這個字"
runp 'grep -rn "key" .' 3
