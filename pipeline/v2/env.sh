# pipeline/v2/env.sh
# 錄屏、對齊、QC 的 shell 會先讀這個檔。
# 把 config.example.env 複製成 config.env（不要 commit），填上這台機器的路徑。
# 金鑰不要寫在這裡。配音只讀套件 .env 裡的 OPENROUTER_API_KEY。

_env_self=${BASH_SOURCE[0]}
_V2=$(cd "$(dirname "$_env_self")" && pwd)
if [ -f "$_V2/config.env" ]; then
  set -a
  # shellcheck disable=SC1091
  . "$_V2/config.env"
  set +a
fi

: "${SEC_SERIES:?請設定 SEC_SERIES。見 pipeline/v2/config.example.env}"
: "${KIT:?請設定 KIT，指到 v1 的 windows-kit。見 pipeline/v2/config.example.env}"
: "${R2:=$_V2/align_qc}"
: "${SEC_LAB:=$SEC_SERIES/lab}"
: "${SEC_INBOX:=$SEC_SERIES/inbox}"
: "${REC_DIR:=$_V2/recording}"
: "${GHIDRA_INSTALL_DIR:=/opt/ghidra}"
# 錄屏裡「裝錯版本、被拒絕」的那一份。旁白仍會講 12.2，路徑不要寫死。
: "${GHIDRA_REJECTED:=/opt/ghidra-rejected}"
: "${JAVA_HOME:=/opt/java}"
# 實驗機上的共用根目錄。下面會有 lab/、vm/、keys/。不是登入者的家目錄。
: "${FENRIS_ROOT:=$SEC_LAB/fenris-root}"
: "${FENRIS_HOME:=$FENRIS_ROOT/labuser}"

export SEC_SERIES KIT R2 SEC_LAB SEC_INBOX REC_DIR GHIDRA_INSTALL_DIR GHIDRA_REJECTED JAVA_HOME FENRIS_ROOT FENRIS_HOME
export PSUSER="${PSUSER:-roy}"
