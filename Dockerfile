# Do not change the base image
FROM python:3.8
COPY . /app

ENV OPENCV_VERSION="4.5.1"
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /opt/build
RUN apt -y update && \
apt -y install build-essential cmake git libgtk-3-dev pkg-config libavcodec-dev libavformat-dev libswscale-dev libv4l-dev libxvidcore-dev libx264-dev openexr libatlas-base-dev libopenexr-dev libgstreamer-plugins-base1.0-dev libgstreamer1.0-dev python3-dev python3-numpy libtbbmalloc2  libtbb-dev libjpeg-dev libpng-dev libtiff-dev libdc1394-dev gfortran && \
mkdir ~/opencv_build && \
cd ~/opencv_build && \
git clone https://github.com/opencv/opencv.git && \
git clone https://github.com/opencv/opencv_contrib.git && \
mkdir -p ~/opencv_build/opencv/build && \
cd ~/opencv_build/opencv/build && \
cmake -D CMAKE_BUILD_TYPE=Release -D CMAKE_INSTALL_PREFIX=/usr/local -D INSTALL_C_EXAMPLES=ON -D INSTALL_PYTHON_EXAMPLES=ON -D OPENCV_GENERATE_PKGCONFIG=ON -D BUILD_EXAMPLES=ON -D OPENCV_EXTRA_MODULES_PATH=~/opencv_build/opencv_contrib/modules .. && \
make -j2 && \
make install

WORKDIR /app
RUN /bin/bash -c 'pip3 install -r requirements.txt'
CMD ["python3", "program.py"]
