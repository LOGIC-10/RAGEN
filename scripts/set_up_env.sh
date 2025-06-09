export http_proxy=http://sys-proxy-rd-relay.byted.org:8118 
export https_proxy=http://sys-proxy-rd-relay.byted.org:8118 
export no_proxy=byted.org

cd /opt/tiger/RAGEN

git submodule init
git submodule update

pip3 install -e .

cd ..

sudo rm -rf verl 

git clone https://github.com/volcengine/verl.git

cd verl
git fetch origin
git checkout 1e47e41

pip3 install -e .




cd /opt/tiger/RAGEN
pip3 install -e .
pip install torch==2.6.0
pip3 install flash-attn --no-build-isolation
pip install flashinfer-python
pip install -r requirements.txt


cd /opt/tiger/CriticSearch
pip install -e .
bash ./generate_settings.sh

echo
echo "✅  所有步骤执行完毕，RAGEN 环境已配置完成！"
