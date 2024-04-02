FROM nvcr.io/nvidia/pytorch:22.06-py3

# SET non-interactive mode and install tzdata
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && apt-get install -y tzdata

# Install dependencies
RUN apt-get install -y \
    git \
    vim \
    wget \
    curl \
    unzip \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgl1-mesa-glx \
    libgl1 \
    libopencv-dev

# Install python dependencies
RUN pip install --upgrade pip
RUN pip install sahi yolov5==7.0.4

# Uninstall and install opencv as user
RUN pip uninstall -y opencv-python && pip install --user opencv-python

RUN ls

# to handle openmpi error for pytorch
ENV PATH="${PATH}:/opt/hpcx/ompi/bin"
ENV LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:/opt/hpcx/ompi/lib"
RUN apt install -y libopenblas-base libopenmpi-dev libboost-all-dev

# to handle _imagingft C module error
RUN pip uninstall pillow -y
RUN apt install -y libfreetype6-dev
RUN pip install pillow python-multipart

# install fastapi server utils
RUN pip install fastapi[all] kafka-python

WORKDIR /workspace/app
