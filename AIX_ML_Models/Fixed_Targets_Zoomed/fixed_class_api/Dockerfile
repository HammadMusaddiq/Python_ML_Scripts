FROM nvcr.io/nvidia/pytorch:22.06-py3

RUN apt update

RUN DEBIAN_FRONTEND=noninteractive apt-get -y install tzdata

RUN apt install -y \
    python3-pip python3-dev git curl wget unzip \
    libgl1-mesa-glx libglib2.0-0 libsm6 libxext6 libxrender-dev \
    libgl1-mesa-glx \
    libgl1 \
    libopencv-dev

RUN pip install --upgrade pip
RUN pip install ultralytics==8.0.22 fastapi[full]
RUN pip install opencv-python==4.2.0.32
RUN pip install uvicorn

# to handle openmpi error for pytorch
ENV PATH="${PATH}:/opt/hpcx/ompi/bin"
ENV LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:/opt/hpcx/ompi/lib"
RUN apt install -y libopenblas-base libopenmpi-dev libboost-all-dev

# to handle _imagingft C module error
RUN pip uninstall pillow -y
RUN apt install -y libfreetype6-dev
RUN pip install pillow python-multipart

RUN pip install python-multipart

WORKDIR /workspace/app

# RUN ls

# ENTRYPOINT [ "/bin/bash" ]
