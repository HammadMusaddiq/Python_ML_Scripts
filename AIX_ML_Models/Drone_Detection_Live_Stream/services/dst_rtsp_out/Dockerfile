FROM nvcr.io/nvidia/deepstream:6.1-devel

RUN apt-key del 7fa2af80
RUN apt-key adv --fetch-keys http://developer.download.nvidia.com/compute/cuda/repos/ubuntu1604/x86_64/3bf863cc.pub

RUN apt-get update && apt-get install -y \
    sudo build-essential cmake ffmpeg g++ libglib2.0-dev libglib2.0-dev-bin libtool m4 autoconf \
    automake libgirepository1.0-dev libcairo2-dev apt-transport-https ca-certificates python-dev \
    python3-gi python3-gst-1.0 libopencv-dev python3-dev python3 python3-pip python-gi-dev \
    libgstrtspserver-1.0-0 gstreamer1.0-rtsp gobject-introspection gir1.2-gst-rtsp-server-1.0
RUN update-ca-certificates
RUN pip3 install --upgrade pip

WORKDIR /root/app/

RUN echo "Installing pyds..." && \
    mkdir -p /tmp/pyds && \
    cd /tmp/pyds && \
    git clone https://github.com/NVIDIA-AI-IOT/deepstream_python_apps.git deepstream_python_apps && \
    cd deepstream_python_apps && \
    git checkout tags/v1.1.3 && \
    git submodule update --init && \
    cd 3rdparty/gst-python/ && \
    ./autogen.sh && make -j6 && make install && \
    cd ../../bindings && \
    mkdir -p build && cd build && \
    cmake -DPYTHON_MAJOR_VERSION=3 -DPYTHON_MINOR_VERSION=8 -DDS_VERSION=6.1 -DDS_PATH=/opt/nvidia/deepstream/deepstream-6.1/ .. && \
    make -j6 && \
    pip3 install pyds-*-py3-none-linux_x86_64.whl && \
    cd /root/app/ && \
    rm -rf /tmp/pyds


COPY dst_rtsp_out/app/plugins /app/plugins
#RUN make -j6 -C /app/plugins/yolov7_custom_parser

ENV DISPLAY=${DISPLAY}

COPY dst_rtsp_out/app/requirements.txt /app/requirements.txt
RUN pip3 install -r /app/requirements.txt

COPY dst_rtsp_out/app /app
WORKDIR /app

# ENV LD_PRELOAD=/app/configs/libRetinafaceDecoder.so:/app/configs/libArcFaceDecoder.so

# RUN apt remove gstreamer1.0-plugins-ugly -y

# CMD [ "python3", "main.py" ]
