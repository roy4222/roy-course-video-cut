. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
cd $SEC_LAB/mit
rm -f g_debian g_ubuntu 2>/dev/null; sudo rm -f g_ubuntu
say "機器人映像的編譯選項：什麼都不加，預設會開哪些？"
runp 'gcc --version | head -1; gcc -O2 guard.c -o g_debian' 2.5
runp 'checksec g_debian 2>&1 | grep -E "RELRO|Stack|FORTIFY"' 3
say "同一份碼，換 Ubuntu 24.04 的 gcc（ROS 2 Jazzy 的底）"
runp 'sudo docker run --rm -v $PWD:/w -w /w lab/ubuntu-gcc gcc -O2 guard.c -o g_ubuntu' 4
runp 'checksec g_ubuntu 2>&1 | grep -E "RELRO|Stack|FORTIFY"' 3
say "一樣的程式，換發行版預設就差一層金絲雀"
say "結論：別賭預設，在 CMake 裡明寫 -fstack-protector-strong"
