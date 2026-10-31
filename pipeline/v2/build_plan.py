"""大綱片段（2026-10-31 匯出）。

匯出在第 10 集的字串中間斷掉。這裡只留完整的第 1–9 集。
全季大綱在課程計畫頁，見倉庫根目錄 COURSES.md。
"""
import json
C161="https://fa25.cs161.org/"; P161="https://fa25.cs161.org/proj1/"
C155="https://cs155.stanford.edu/syllabus.html"; P155="https://cs155.stanford.edu/hw_and_proj/proj1.pdf"
M566="https://css.csail.mit.edu/6.858/2024/"; L566="https://css.csail.mit.edu/6.858/2024/labs/lab1.html"
CSAPP="https://csapp.cs.cmu.edu/3e/labs.html"; PWN="https://pwn.college/"; LUM="https://pwn.college/linux-luminarium/"
BANDIT="https://overthewire.org/wargames/bandit/"; PICO="https://picoctf.org/"; NIGHT="https://guyinatuxedo.github.io/"
LO="https://www.youtube.com/playlist?list=PLhixgUqwRTjxglIswKp9mpkfPNfHkzyeN"; TB="https://textbook.cs161.org/"
E=[]
def ep(n,stage,title,goal,pre,demo,real,gen,course,link,hw,robot=""):
    E.append(dict(ep=n,stage=stage,title=title,goal=goal,prereq=pre,demo=demo,real_images=real,gen_images=gen,course=course,course_link=link,homework=hw,robot_tie_in=robot))
S0,S1,S2,S3,S4="S0 零基礎","S1 銜接","S2 課程：記憶體安全","S3 課程：隔離與系統防禦","S4 作業實戰與總結"
ep(1,S0,"資安到底在保護什麼？從一台導盲機器狗說起","能用「資產／攻擊者／能力」三句話描述威脅模型","無","在終端機 `ssh` 連進 Docker 容器、`ls -l` 看到別人可讀的設定檔","CS161 Lec1 投影片首頁截圖、6.566 LEC1 課表截圖","機器狗被入侵的情境插圖；CIA 三角圖","CS161 Lec1 Security Principles；6.566 LEC1 Threat models",C161,"寫出 FenrisOS 的 3 個資產與 3 種攻擊者","FenrisOS：誰能讓 Go2 走錯路？")
ep(2,S0,"電腦怎麼跑一支程式：CPU、記憶體、指令","知道程式＝放在記憶體裡的位元組，CPU 一條一條取來執行","EP01","`python3 -c` 與 `gcc hello.c` 對照；`xxd hello | head` 看到機器碼","CS:APP 第 1 章 hello 程式生命週期圖（引用來源）","CPU 取指令—執行的流程插畫；廚師照食譜做菜比喻圖","CS:APP Ch1；CS161 Discussion 0 (61C Review)",CSAPP,"在自己電腦編譯 hello.c，用 xxd 找到字串 hello","")
ep(3,S0,"Linux 終端機第一課：在黑畫面裡走路","會用 pwd/ls/cd/cat/less/grep 和管線","EP02","實機錄屏：pwn.college Linux Luminarium 第一關畫面＋box 上真實指令","pwn.college Linux Luminarium 頁面截圖；Bandit Level 0 頁面截圖","目錄樹＝資料夾大樓的等距插圖","pwn.college Linux Luminarium；OverTheWire Bandit 0→5",LUM,"破 Bandit Level 0→5","在 Go2 的 Jetson 上找 ROS 2 log 檔")
ep(4,S0,"使用者、權限與 sudo：誰可以碰哪個檔案","讀得懂 `-rwxr-x---`，知道 root 與 setuid 是什麼","EP03","`id`、`chmod`、`sudo`、`find / -perm -4000` 列出 setuid 程式","CS155 Lec5 OS Security 投影片截圖（setuid 頁）","權限 9 格門鎖圖解","CS155 Lec5 Security Principles & OS Security；Bandit 6→12",C155,"破 Bandit 6→12；列出自己電腦的 setuid 程式","ROS 2 節點用 root 跑的風險")
ep(5,S0,"給 Python 使用者的 C 語言","會寫、編譯、執行含陣列與字串的 C 程式","EP03","VS Code 錄屏：同一個功能 Python vs C 寫法並排、`gcc -Wall` 編譯錯誤","CS:APP／15-213 課程頁截圖","「Python 有保母、C 沒有」對照插圖","CS:APP Ch2 前半；15-213 先修",CSAPP,"用 C 寫一個反轉字串程式","")
ep(6,S0,"指標：記憶體地址就是門牌號碼","懂 `&`、`*`、陣列與指標的關係","EP05","`printf(\"%p\")` 印出變數地址；gdb `print &x` 首次登場","CS161 Lec2 投影片中記憶體配置圖截圖","門牌號碼街道圖（地址→盒子）","CS161 Lec2 x86 Assembly and Call Stack（先修概念）",C161,"畫出 int a[4] 在記憶體中的位置","")
ep(7,S0,"位元、十六進位與小端序：看懂 0x41414141","會 hex/decimal 換算，懂 little-endian","EP06","`xxd`、`python3 -c 'print(hex(65))'`、`struct.pack('<I',...)`","CS:APP Data Lab 頁面截圖","bytes 倒著放的動畫圖","CS:APP Ch2；Data Lab",CSAPP,"picoCTF 入門 General Skills 3 題","IMU 封包解析也是小端序")
ep(8,S0,"一支程式在記憶體裡的樣子：text、heap、stack","能指出程式碼、全域變數、heap、stack 各在哪","EP06–07","`cat /proc/self/maps`、印出區域變數與 malloc 地址比較","CS161 Lec2 Memory layout 投影片截圖；textbook Ch2 圖","記憶體大樓剖面插圖（stack 往下長）","CS161 Lec2；textbook Ch2",TB,"寫程式印出 4 個區域的地址並排序","")
ep(9,S1,"組合語言看得懂就好：x86-64 十個指令","讀得懂 mov/add/cmp/jmp/call/ret","EP08","`objdump -d -M intel`、Compiler Explorer 錄屏 C↔組語對照","CS161 x86/GDB Cheat Sheet 截圖；CS:APP Ch3 圖","暫存器＝CPU 手上的 16 個小盒子插圖","CS161 Lec2；CS:APP Ch3",C161,"手翻譯 3 段小組語成 C","")

# 第 10 集起的列在匯出裡不完整，沒有放進來。
if __name__ == "__main__":
    print(json.dumps(E, ensure_ascii=False, indent=1))
    print("fragment only: SEC01-SEC09", file=__import__("sys").stderr)
