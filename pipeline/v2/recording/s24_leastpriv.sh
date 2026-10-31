. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
say "最小權限 demo：一個故意有 bug 的「看照片」服務（玩具）"
runp "grep -n 'path =' dog_photo_service.py" 2
say "正常用法：給檔名，回照片"
runp 'python3 dog_photo_service.py today.jpg' 2
say "bug：檔名裡塞 ../ 就能走出照片夾"
runp 'python3 dog_photo_service.py ../house/owner_notes.txt' 3
say "它用的是「我」的全部權限，所以家裡的東西都讀得到"
say "最小權限：只給它照片夾（唯讀）、不給網路、換成 uid 1234"
runp "grep -E 'unshare|ro-bind' sandbox.sh" 3
runp './sandbox.sh python3 /srv/dog_photo_service.py ../house/owner_notes.txt' 3
say "bug 還在，但它根本看不到那個檔案"
runp "./sandbox.sh python3 -c \"import os,socket; print('家目錄：', os.path.exists('/home'));
try: socket.create_connection(('1.1.1.1',80),timeout=2)
except OSError as e: print('連網路：失敗', type(e).__name__)\"" 3
say "最小權限不會讓 bug 消失，但讓 bug 能造成的傷害變小"
