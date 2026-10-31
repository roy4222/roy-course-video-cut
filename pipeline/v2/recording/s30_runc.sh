. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
cd $SEC_LAB/iso
say "最後：錄這集的機器本身，容器執行器 runc 是哪一版？"
runp "sudo docker version --format 'Docker {{.Server.Version}}'; sudo runc --version | head -1" 3
runp "dpkg -l runc | tail -1 | awk '{print \$2, \$3}'" 3
say "對照 NVD 與 Debian 安全追蹤：這一版在 CVE-2025-31133 的受影響名單上"
say "容器邊界的安全，取決於你多久更新一次 runc"
