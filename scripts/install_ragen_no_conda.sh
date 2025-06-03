#!/bin/bash

# 出现错误时立即退出
set -e

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # 无颜色

# 打印步骤函数
print_step() {
    echo -e "${BLUE}[Step] ${1}${NC}"
}

export http_proxy=http://sys-proxy-rd-relay.byted.org:8118 
export https_proxy=http://sys-proxy-rd-relay.byted.org:8118 
export no_proxy=byted.org

# 检查是否存在 CUDA-capable GPU
check_cuda() {
    if command -v nvidia-smi &> /dev/null; then
        echo "CUDA GPU detected"
        return 0
    else
        echo "No CUDA GPU detected"
        return 1
    fi
}

main() {
    # 假设当前目录已经是 ragen 项目根目录（包含 setup.py）
    # 如果需要先 clone，请放在这里，例如：
    # print_step "Cloning ragen 仓库..."
    # git clone git@github.com:ZihanWang314/ragen.git
    # cd ragen

    # -------------------------------------------------------------------------
    # 1. 初始化并安装 verl 子模块（固定到指定版本）
    # -------------------------------------------------------------------------
    print_step "初始化并更新 verl 子模块到指定版本 (1e47e41)..."
    git submodule init
    git submodule update

    cd verl
    # 如果本地没有该 commit，需要从远端抓取
    git fetch origin
    git checkout 1e47e41           # 切换到指定版本
    sudo pip3 install -e .
    cd ..

    # -------------------------------------------------------------------------
    # 2. 安装 ragen 包本身（可编辑模式）
    # -------------------------------------------------------------------------
    print_step "安装 ragen 包（可编辑模式）..."
    sudo pip3 install -e .

    # -------------------------------------------------------------------------
    # 3. 根据是否有 GPU，安装对应的 PyTorch
    # -------------------------------------------------------------------------
    if check_cuda; then
        print_step "检测到 CUDA → 安装带 CUDA 的 PyTorch..."

        if command -v nvcc &> /dev/null; then
            nvcc_version=$(nvcc --version | grep "release" | awk '{print $6}' | cut -c2-)
            nvcc_major=$(echo "$nvcc_version" | cut -d. -f1)
            nvcc_minor=$(echo "$nvcc_version" | cut -d. -f2)
            echo "Detected nvcc version: $nvcc_version"

            # 要求 CUDA ≥ 12.4
            if [[ "$nvcc_major" -gt 12 || ( "$nvcc_major" -eq 12 && "$nvcc_minor" -ge 4 ) ]]; then
                echo "CUDA ≥ 12.4，跳过 Toolkit 安装"
                export CUDA_HOME=${CUDA_HOME:-$(dirname "$(dirname "$(which nvcc)")")}
            else
                print_step "当前 CUDA 版本 < 12.4，请在镜像中预先安装 CUDA 12.4"
                # 如果需要在此处用系统包管理器安装，可以改成类似：
                # sudo apt-get update && sudo apt-get install -y cuda-toolkit-12-4
                export CUDA_HOME=/usr/local/cuda-12.4
            fi
        else
            print_step "未检测到 nvcc，假设容器中已有 CUDA Runtime"
            export CUDA_HOME=/usr/local/cuda
        fi

        print_step "使用 pip 安装 torch==2.6.0（CUDA 12.4）..."
        sudo pip3 install torch==2.6.0
        print_step "安装 flash-attn..."
        sudo pip3 install flash-attn --no-build-isolation
    else
        print_step "未检测到 CUDA → 安装 CPU-only PyTorch..."
        sudo pip3 install torch==2.6.0
    fi

    # -------------------------------------------------------------------------
    # 4. 安装其余依赖
    # -------------------------------------------------------------------------
    print_step "安装其他 Python 依赖..."
    sudo pip3 install -r requirements.txt

    # -------------------------------------------------------------------------
    # 5. 安装CriticSearch相关的依赖
    # -------------------------------------------------------------------------
    cd /opt/tiger/qinyu.luo/CriticSearch
    sudo pip install -e .

    # 从环境变量中生成settings.yaml文件
    ./generate_settings.sh


    cd /opt/tiger/RAGEN


    echo -e "${GREEN}✅ 安装完成！${NC}"
    echo "后续直接在容器内运行即可，无需 Conda。"
}

main