. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
R=$FENRIS_HOME
chmod 644 $R/fenris_ws/src/guide_dog/config/cloud_secret.yaml
sudo rm -f $R/fenris_ws/scripts/startup.sh
cat > $R/fenris_ws/scripts/startup.sh <<'X'
#!/bin/bash
# 開機時由 root 執行（模擬 systemd service）
echo "[startup] 啟動 guide_dog ... 執行身分: $(id -un)"
X
chmod 755 $R/fenris_ws/scripts/startup.sh; chmod 644 $R/fenris_ws/log/robot.log; rm -f $R/fenris_ws/log/errors.txt; rm -rf $R/.ssh /tmp/evil
