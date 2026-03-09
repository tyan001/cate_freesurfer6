FROM ubuntu:focal

ENV DEBIAN_FRONTEND=noninteractive \
    FREESURFER_HOME=/usr/local/freesurfer \
    FSLDIR=/usr/local/fsl \
    SUBJECTS_DIR=/usr/local/freesurfer/subjects \
    FUNCTIONALS_DIR=/usr/local/freesurfer/sessions \
    FSLOUTPUTTYPE=NIFTI_GZ \
    FSLMULTIFILEQUIT=TRUE \
    FSF_OUTPUT_FORMAT=nii.gz \
    OS=Linux \
    CC=/usr/bin/gcc \
    CXX=/usr/bin/g++ \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    bc \
    build-essential \
    ca-certificates \
    curl \
    dc \
    file \
    gawk \
    mesa-utils \
    pulseaudio \
    libquadmath0 \
    libgtk2.0-0 \
    lbzip2 \
    libglu1-mesa \
    libgomp1 \
    libjpeg62 \
    libncurses5 \
    libsm6 \
    libx11-6 \
    libxext6 \
    libxft2 \
    libxmu6 \
    libxrender1 \
    libxt6 \
    perl \
    python3 \
    python2 \
    r-base \
    tar \
    tcsh \
    unzip \
    wget \
    zlib1g-dev \
    vim \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# FreeSurfer 6.0
RUN cd /usr/local && \
    wget -q https://surfer.nmr.mgh.harvard.edu/pub/dist/freesurfer/6.0.0/freesurfer-Linux-centos6_x86_64-stable-pub-v6.0.0.tar.gz && \
    tar -xzf freesurfer-Linux-centos6_x86_64-stable-pub-v6.0.0.tar.gz && \
    rm freesurfer-Linux-centos6_x86_64-stable-pub-v6.0.0.tar.gz

# FreeSurfer 6 scripts use Python 2 syntax; symlink python -> python2 inside FS bin
# (FREESURFER_HOME/bin is first in PATH, so FS scripts will use python2)
RUN ln -s /usr/bin/python2 /usr/local/freesurfer/bin/python

# Matlab Runtime 2012b (needed by FreeSurfer 6 hippocampal subfield module)
COPY fs_install_mcr.sh /usr/local/bin/fs_install_mcr.sh
RUN chmod +x /usr/local/bin/fs_install_mcr.sh && \
    /usr/local/bin/fs_install_mcr.sh R2012b

# FSL
RUN wget -q https://fsl.fmrib.ox.ac.uk/fsldownloads/fslconda/releases/fslinstaller.py && \
    python3 ./fslinstaller.py -d /usr/local/fsl/ --skip_ssl_verify && \
    rm fslinstaller.py

# R package
ENV CC=/usr/bin/gcc \
    CXX=/usr/bin/g++
RUN Rscript -e "install.packages('oro.nifti', repos='http://cran.rstudio.com')"

# PATH and shell setup
ENV FSLTCLSH=$FSLDIR/bin/fsltclsh \
    FSLWISH=$FSLDIR/bin/fslwish 
    
ENV PATH=$FREESURFER_HOME/bin:$PATH

RUN echo 'source $FREESURFER_HOME/SetUpFreeSurfer.sh' >> /etc/bash.bashrc && \
    echo 'source $FSLDIR/etc/fslconf/fsl.sh' >> /etc/bash.bashrc

# Workspace and scripts
RUN mkdir -p /workspace/data
COPY quantifyHippocampalSubfields.sh /usr/local/bin/quantifyHippocampalSubfields.sh
RUN chmod +x /usr/local/bin/quantifyHippocampalSubfields.sh

COPY mri_scripts/ /workspace/mri_scripts/
COPY suvr_scripts/ /workspace/suvr_scripts/

# COPY license.txt /usr/local/freesurfer/license.txt

WORKDIR /workspace
CMD ["/bin/bash"]