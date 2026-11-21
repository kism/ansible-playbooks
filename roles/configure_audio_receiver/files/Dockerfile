# Cross-compiles AirPlay 2 shairport-sync + nqptp for armhf (Pi 2) on an amd64 host, no QEMU needed
# ponytail: Debian armhf is ARMv7, these binaries won't run on a Pi 1/Zero (Raspbian ARMv6)
FROM debian:trixie AS build

ENV DEBIAN_FRONTEND=noninteractive
ENV HOST=arm-linux-gnueabihf

ARG SHAIRPORT_VERSION
ARG NQPTP_VERSION

RUN dpkg --add-architecture armhf && apt-get update && apt-get -y --no-install-recommends install \
    build-essential crossbuild-essential-armhf git ca-certificates autoconf automake libtool pkgconf systemd-dev \
    xxd libplist-utils binutils-arm-linux-gnueabihf \
    libpopt-dev:armhf libconfig-dev:armhf libasound2-dev:armhf libavahi-client-dev:armhf \
    libssl-dev:armhf libsoxr-dev:armhf libplist-dev:armhf libsodium-dev:armhf uuid-dev:armhf \
    libgcrypt20-dev:armhf libavutil-dev:armhf libavcodec-dev:armhf libavformat-dev:armhf \
    libswresample-dev:armhf \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /src
RUN git clone --depth 1 --branch ${NQPTP_VERSION} https://github.com/mikebrady/nqptp.git \
    && cd nqptp && autoreconf -fi && ./configure --host=${HOST} --with-systemd-startup && make && make install

RUN git clone --depth 1 --branch ${SHAIRPORT_VERSION} https://github.com/mikebrady/shairport-sync.git \
    && cd shairport-sync && autoreconf -fi \
    && ./configure --host=${HOST} --sysconfdir=/etc --with-alsa --with-soxr --with-avahi --with-ssl=openssl --with-systemd-startup --with-airplay-2 \
    && make && make install

# Can't run an arm binary here, so check the build flags and arch instead
RUN grep -q "define CONFIG_AIRPLAY_2 1" shairport-sync/config.h \
    && ${HOST}-readelf -h /usr/local/bin/shairport-sync /usr/local/bin/nqptp | grep -c "Machine:.*ARM" | grep -qx 2

# Runtime deps for the target, taken from what the binaries actually link against
RUN ${HOST}-readelf -d /usr/local/bin/shairport-sync /usr/local/bin/nqptp \
    | sed -n 's/.*Shared library: \[\(.*\)\]/\1/p' | sort -u \
    | xargs -I{} dpkg -S "/usr/lib/${HOST}/{}" | cut -d: -f1 | sort -u > /src/runtime-packages.txt

FROM scratch
COPY --from=build /usr/local/bin/shairport-sync /usr/local/bin/nqptp /src/runtime-packages.txt /
COPY --from=build /usr/lib/systemd/system/shairport-sync.service /usr/lib/systemd/system/nqptp.service /
