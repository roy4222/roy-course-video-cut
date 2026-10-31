. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
say "LiDAR 點雲：專案裡藏了一個 WebAssembly 解碼器"
run 'file go2_ros2_sdk/go2_robot_sdk/external_lib/libvoxel.wasm; ls -l go2_ros2_sdk/go2_robot_sdk/external_lib/libvoxel.wasm | cut -d" " -f5-' 3
run '.venv/bin/python -c "import wasmtime as w;m=w.Module.from_file(w.Engine(),\"go2_ros2_sdk/go2_robot_sdk/external_lib/libvoxel.wasm\");print(\"exports:\",[e.name for e in m.exports])"' 3.5
say "名字被壓成 a、b、c… 看不出意思，只能當黑盒子呼叫"
say "後來社群把格式讀懂了，改用純 Python：LZ4 解壓 + 一個 bit 一格"
run 'grep -n "lz4\|def bits_to_points\|0x800\|0x10" unitree_webrtc_connect/unitree_webrtc_connect/lidar/lidar_decoder_native.py' 4
say "自己做一包假資料，用同樣格式解回來（純離線）"
run '.venv/bin/python lidar_demo.py' 5
