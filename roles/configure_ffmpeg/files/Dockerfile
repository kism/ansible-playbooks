FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

ARG FFMPEG_VERSION=9.0.2

RUN apt-get update && apt-get -y --no-install-recommends install \
    build-essential curl ca-certificates python3 python-is-python3 \
    ninja-build meson git \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY ./build-ffmpeg /app/build-ffmpeg
COPY src /app/src

RUN AUTOINSTALL=yes /app/build-ffmpeg --build --enable-gpl-and-non-free --full-static --ffmpeg-version=${FFMPEG_VERSION}

RUN ldd /app/workspace/bin/ffmpeg 2>&1 | grep -q "not a dynamic executable" && \
    ldd /app/workspace/bin/ffprobe 2>&1 | grep -q "not a dynamic executable"
