. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
say "機器人實戰：Go2 SDK 附帶的 CycloneDDS 函式庫（開源）"
run 'ls -lh sdk/libddsc.so.0' 1.5
run 'rea inspect-native-exports sdk/libddsc.so.0 --format json | nr coverage' 3
run 'rea inspect-native-exports sdk/libddsc.so.0 --format json | python3 -c "import json,sys;[print(e[\"name\"]) for e in json.load(sys.stdin)[\"normalized_result\"][\"exports\"] if e[\"name\"].startswith((\"dds_create_\",\"dds_write\",\"dds_take\"))]" | sort | head -16' 5
say "1304 個對外函式，1.3 秒列完。ROS 2 底層常用的 DDS，就長這樣"
