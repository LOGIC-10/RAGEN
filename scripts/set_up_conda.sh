export http_proxy=http://sys-proxy-rd-relay.byted.org:8118 
export https_proxy=http://sys-proxy-rd-relay.byted.org:8118 
export no_proxy=byted.org
cd ~

wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh
bash ~/miniconda.sh -b -p $HOME/miniconda3

echo 'export PATH="$HOME/miniconda3/bin:$PATH"' >> ~/.bashrc
