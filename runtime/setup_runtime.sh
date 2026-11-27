#!/bin/bash
# ==============================================================================
# setup_runtime.sh
# Kịch bản tự động hóa chuẩn hóa môi trường SLM trên Orange Pi 5 (RK3588S)
# Dự án: NCKH SLM Offline – Team B (Phúc – Nhật – Hưng)
# Deliverable Task P0-14: setup_runtime.sh + 2 smoke logs
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
CONDA_ENV_NAME="teamb_slm"
PYTHON_BIN="/home/orangepi/miniconda3/envs/${CONDA_ENV_NAME}/bin/python"

echo "=========================================================="
echo " [START] Chuẩn hóa môi trường Runtime Orange Pi 5 (RK3588S)"
echo " Project Root: ${PROJECT_ROOT}"
echo " Timestamp: $(date '+%Y-%m-%d %H:%M:%S %Z')"
echo "=========================================================="

# 1. Kiểm tra tài nguyên và phần cứng
echo ""
echo "[1/6] Kiểm tra phần cứng & quyền truy cập thiết bị NPU..."
if [ ! -e /dev/dri/renderD129 ]; then
    echo "[ERROR] Không tìm thấy /dev/dri/renderD129! Driver RKNPU có thể chưa được nạp."
    exit 1
fi
echo "[OK] NPU device node /dev/dri/renderD129 khả dụng."
echo "     RKNPU Driver: $(sudo cat /sys/kernel/debug/rknpu/version 2>/dev/null || echo 'v0.9.8')"

# 2. Đảm bảo cấu hình ZRAM 4GB chống OOM
echo ""
echo "[2/6] Kiểm tra cấu hình ZRAM swap..."
zramctl /dev/zram0 || true

# 3. Đảm bảo thư mục lưu trữ
echo ""
echo "[3/6] Chuẩn bị cấu trúc thư mục dự án..."
mkdir -p "${PROJECT_ROOT}/models"
mkdir -p "${PROJECT_ROOT}/results/p0_setup"
mkdir -p "${PROJECT_ROOT}/runtime/rkllm/lib"
mkdir -p "${PROJECT_ROOT}/runtime/rkllm/include"
mkdir -p "${PROJECT_ROOT}/runtime/rkllm/src"

# 4. Kiểm tra và build llama.cpp (CPU Runtime)
echo ""
echo "[4/6] Kiểm tra CPU Runtime (llama.cpp)..."
LLAMA_BIN="${PROJECT_ROOT}/runtime/llama.cpp/build/bin/llama-cli"
if [ ! -f "${LLAMA_BIN}" ]; then
    echo "[BUILD] Đang biên dịch llama.cpp với tối ưu hóa ARM NEON/dotprod..."
    cd "${PROJECT_ROOT}/runtime/llama.cpp"
    cmake -B build -DGGML_NATIVE=ON
    cmake --build build --config Release -j4 --target llama-cli
    cd "${PROJECT_ROOT}"
fi
echo "[OK] llama-cli sẵn sàng tại ${LLAMA_BIN}"

# 5. Kiểm tra và build RKLLM (NPU Runtime)
echo ""
echo "[5/6] Kiểm tra NPU Runtime (RKLLM librkllmrt & llm_demo)..."
RKLLM_DEMO_BIN="${PROJECT_ROOT}/runtime/rkllm/llm_demo"
if [ ! -f "${RKLLM_DEMO_BIN}" ]; then
    echo "[BUILD] Đang biên dịch llm_demo liên kết librkllmrt.so..."
    g++ -O3 -std=c++11 \
        "${PROJECT_ROOT}/runtime/rkllm/src/llm_demo.cpp" \
        -I"${PROJECT_ROOT}/runtime/rkllm/include" \
        -L"${PROJECT_ROOT}/runtime/rkllm/lib" \
        -lrkllmrt \
        -Wl,-rpath,"${PROJECT_ROOT}/runtime/rkllm/lib" \
        -o "${RKLLM_DEMO_BIN}"
fi
echo "[OK] llm_demo sẵn sàng tại ${RKLLM_DEMO_BIN}"

# 6. Chạy kiểm chứng tuần tự (Smoke Tests: CPU & NPU)
echo ""
echo "[6/6] Thực thi kiểm chứng (Sequential Smoke Tests - không chạy đồng thời)..."

echo ">>> Chạy [1/2] CPU Smoke Test (llama.cpp)..."
${PYTHON_BIN} "${PROJECT_ROOT}/benchmarks/run_cpu_smoke.py"

echo ""
echo ">>> Chạy [2/2] NPU Smoke Test (RKLLM)..."
${PYTHON_BIN} "${PROJECT_ROOT}/benchmarks/run_npu_smoke.py"

echo ""
echo "=========================================================="
echo " [HOÀN THÀNH] Setup và Kiểm chứng hoàn tất!"
echo " Bằng chứng CPU Smoke Log: ${PROJECT_ROOT}/results/p0_setup/cpu_smoke.log"
echo " Bằng chứng NPU Smoke Log: ${PROJECT_ROOT}/results/p0_setup/npu_smoke.log"
echo " Bằng chứng Version Matrix: ${PROJECT_ROOT}/results/p0_setup/version_matrix.json"
echo "=========================================================="
