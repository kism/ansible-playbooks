# Builds duperemove on the workstation, Debian only packages 0.11
# ponytail: native amd64 build against trixie, targets must be amd64 trixie too
FROM debian:trixie AS build

ENV DEBIAN_FRONTEND=noninteractive

ARG DUPEREMOVE_VERSION

RUN apt-get update && apt-get -y --no-install-recommends install \
    build-essential git ca-certificates pkg-config \
    libglib2.0-dev libsqlite3-dev libxxhash-dev libbsd-dev libblkid-dev libmount-dev uuid-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /src
# Man page is committed, only the binary needs building (make install would want pandoc)
RUN git clone --depth 1 --branch v${DUPEREMOVE_VERSION} https://github.com/markfasheh/duperemove.git \
    && cd duperemove && make VERSION=${DUPEREMOVE_VERSION} duperemove

RUN duperemove/duperemove --version | grep -q "${DUPEREMOVE_VERSION}"

# Runtime deps for the target, taken from what the binary actually links against
RUN readelf -d duperemove/duperemove \
    | sed -n 's/.*Shared library: \[\(.*\)\]/\1/p' \
    | xargs -I{} dpkg -S "*/{}" | cut -d: -f1 | sort -u > /src/runtime-packages.txt

FROM scratch
COPY --from=build /src/duperemove/duperemove /src/duperemove/duperemove.8 /src/runtime-packages.txt /
