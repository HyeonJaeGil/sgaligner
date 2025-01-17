FROM pytorch/pytorch:2.2.2-cuda12.1-cudnn8-devel

# Arguments to build Docker Image using CUDA
ARG USE_CUDA=0
ARG TORCH_ARCH=

ENV AM_I_DOCKER True
ENV BUILD_WITH_CUDA "${USE_CUDA}"
ENV TORCH_CUDA_ARCH_LIST "${TORCH_ARCH}"
ENV CUDA_HOME /usr/local/cuda-12.1/

RUN mkdir -p /home/appuser/sgaligner
COPY . /home/appuser/sgaligner/
WORKDIR  /home/appuser/sgaligner

# RUN git submodule update --recursive

ENV DEBIAN_FRONTEND=noninteractive

RUN apt update
RUN apt install -y \
    build-essential  \
    cmake \
    pkg-config  \
    htop  \
    gedit  \
    wget \
    git \
    unzip  \
    curl \
    vim \
    software-properties-common \
    net-tools \
    iputils-ping
    
RUN apt clean

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN echo "[user]" >> /root/.gitconfig && \
    echo "	email = now9728@gmail.com" >> /root/.gitconfig && \
    echo "	name = HyeonJaeGil" >> /root/.gitconfig

RUN echo "PS1='\[\e]0;\u@\h: \w\a\]${debian_chroot:+($debian_chroot)}\[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]# '\n\
if [ -x /usr/bin/dircolors ]; then\n\
    test -r ~/.dircolors && eval \"\$(dircolors -b ~/.dircolors)\" || eval \"\$(dircolors -b)\"\n\
    alias ls='ls --color=auto'\n\
    alias grep='grep --color=auto'\n\
    alias fgrep='fgrep --color=auto'\n\
    alias egrep='egrep --color=auto'\n\
fi" >> /root/.bashrc

CMD ["/bin/bash"]
