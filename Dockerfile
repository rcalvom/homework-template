FROM texlive/texlive:latest@sha256:4984977ccf5afe883cb382d0163f267de0d029d140bb7a9e8f4c19f0b781d57b

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    default-jre-headless \
    fontconfig \
    ghostscript \
    librsvg2-bin \
    make \
    poppler-utils \
    python3-pip \
    python3-pygments \
    python3-fonttools \
    qpdf \
    unzip \
 && pip install --break-system-packages --no-cache-dir latexminted==0.7.1 \
 && rm -rf /var/lib/apt/lists/*

ARG TARGETARCH
ARG D2_VERSION=0.7.1
ARG D2_AMD64_SHA256=eb172adf59f38d1e5a70ab177591356754ffaf9bebb84e0ca8b767dfb421dad7
ARG D2_ARM64_SHA256=ce3a0b985a8f91335a826c254b3a88736fd81afcdd08b58f6c749d2add6864b0
RUN set -eux; \
    arch="${TARGETARCH:-amd64}"; \
    case "$arch" in \
      amd64) checksum="$D2_AMD64_SHA256" ;; \
      arm64) checksum="$D2_ARM64_SHA256" ;; \
      *) echo "unsupported architecture: $arch" >&2; exit 1 ;; \
    esac; \
    url="https://github.com/terrastruct/d2/releases/download/v${D2_VERSION}/d2-v${D2_VERSION}-linux-${arch}.tar.gz"; \
    curl -fsSL "$url" -o /tmp/d2.tar.gz; \
    echo "$checksum  /tmp/d2.tar.gz" | sha256sum -c -; \
    tar -C /tmp -xzf /tmp/d2.tar.gz; \
    install -m0755 "/tmp/d2-v${D2_VERSION}/bin/d2" /usr/local/bin/d2; \
    rm -rf /tmp/d2.tar.gz "/tmp/d2-v${D2_VERSION}"; \
    d2 --version

ARG VERAPDF=1
ARG VERAPDF_VERSION=1.30.2
ARG VERAPDF_SHA256=6cc6341cb1af644044054b81f00a6590a7918abb18f762243de115258bcad838
RUN set -eux; \
    if [ "$VERAPDF" = "1" ]; then \
      cd /tmp; \
      curl -fsSL "https://software.verapdf.org/releases/1.30/verapdf-greenfield-${VERAPDF_VERSION}-installer.zip" -o verapdf.zip; \
      echo "$VERAPDF_SHA256  verapdf.zip" | sha256sum -c -; \
      unzip -q verapdf.zip; \
      cd "verapdf-greenfield-${VERAPDF_VERSION}"/; \
      printf '%s\n' \
        '<?xml version="1.0" encoding="UTF-8" standalone="no"?>' \
        '<AutomatedInstallation langpack="eng">' \
        '  <com.izforge.izpack.panels.htmlhello.HTMLHelloPanel id="welcome"/>' \
        '  <com.izforge.izpack.panels.target.TargetPanel id="install_dir">' \
        '    <installpath>/opt/verapdf</installpath>' \
        '  </com.izforge.izpack.panels.target.TargetPanel>' \
        '  <com.izforge.izpack.panels.packs.PacksPanel id="sdk_pack_select"/>' \
        '  <com.izforge.izpack.panels.install.InstallPanel id="install"/>' \
        '  <com.izforge.izpack.panels.finish.FinishPanel id="finish"/>' \
        '</AutomatedInstallation>' > auto.xml; \
      java -jar verapdf-izpack-installer-*.jar auto.xml; \
      ln -s /opt/verapdf/verapdf /usr/local/bin/verapdf; \
      cd /tmp; \
      rm -rf verapdf.zip verapdf-greenfield-*; \
      verapdf --version; \
    fi

# The code plate's colours are a Pygments plugin, and Pygments resolves a style
# through its registry rather than from a path -- so PYTHONPATH is not enough
# and the style has to be installed. theme/pygments is the one thing copied
# into an image that otherwise bind-mounts the repository.
COPY theme/pygments /opt/rzstyle
RUN pip install --break-system-packages --no-cache-dir /opt/rzstyle \
 && pygmentize -S rzstyle-light -f latex >/dev/null

WORKDIR /workspace

ENV TEXMFVAR=/tmp/texmf-var

CMD ["make"]
