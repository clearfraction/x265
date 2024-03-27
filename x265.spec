%global gitdate 20240315
%global commit 3cf6c1e53037eb9e198860365712e1bafb22f7c6
%global shortcommit %(c=%{commit}; echo ${c:0:12})  
%global gver .git%{shortcommit}

Summary:    H.265/HEVC encoder
Name:       x265
Group:      Applications/Multimedia
Version:    3.5
Release:    %{commit}
URL:        http://x265.org/
Source0:    https://bitbucket.org/multicoreware/x265_git/get/%{commit}.tar.gz#/%{name}-%{shortcommit}.tar.gz
Patch:      pkgconfig_fix.patch
License:    GPLv2+ and BSD
BuildRequires:  cmake
BuildRequires:  gcc
BuildRequires:  nasm
BuildRequires:  yasm
BuildRequires:  pkg-config
BuildRequires:  numactl-dev

%description
The primary objective of x265 is to become the best H.265/HEVC encoder
available anywhere, offering the highest compression efficiency and the
highest performance on a wide variety of hardware platforms.

%package libs
Summary: H.265/HEVC encoder library
Group: Development/Libraries

%description libs
The primary objective of x265 is to become the best H.265/HEVC encoder
available anywhere, offering the highest compression efficiency and the
highest performance on a wide variety of hardware platforms.

%package dev
Summary: H.265/HEVC encoder library development files
Group: Development/Libraries
Requires: %{name}-libs = %{version}-%{release}

%description dev
The primary objective of x265 is to become the best H.265/HEVC encoder
available anywhere, offering the highest compression efficiency and the
highest performance on a wide variety of hardware platforms.
This package contains the shared library development files.

%prep
%setup -n multicoreware-x265_git-%{shortcommit}
%patch -p1
sed -i 's|set(LIB_INSTALL_DIR lib CACHE STRING "Install location of libraries")|set(LIB_INSTALL_DIR lib64 CACHE STRING "Install location of libraries")|g' source/CMakeLists.txt
mkdir -p build-8 build-10 build-12


%build
export LANG=C.UTF-8
export GCC_IGNORE_WERROR=1
export AR=gcc-ar
export RANLIB=gcc-ranlib
export NM=gcc-nm
export CFLAGS="$CFLAGS -O3 -Ofast -falign-functions=32 -ffat-lto-objects -flto=auto -fno-semantic-interposition -mprefer-vector-width=256 "
export FCFLAGS="$FFLAGS -O3 -Ofast -falign-functions=32 -ffat-lto-objects -flto=auto -fno-semantic-interposition -mprefer-vector-width=256 "
export FFLAGS="$FFLAGS -O3 -Ofast -falign-functions=32 -ffat-lto-objects -flto=auto -fno-semantic-interposition -mprefer-vector-width=256 "
export CXXFLAGS="$CXXFLAGS -O3 -Ofast -falign-functions=32 -ffat-lto-objects -flto=auto -fno-semantic-interposition -mprefer-vector-width=256 "

pushd build-12
    %cmake ../source \
      -DCMAKE_INSTALL_PREFIX='/usr' \
      -DHIGH_BIT_DEPTH='TRUE' \
      -DMAIN12='TRUE' \
      -DEXPORT_C_API='FALSE' \
      -DENABLE_CLI='FALSE' \
      -DENABLE_HDR10_PLUS=YES \
      -DENABLE_SHARED='FALSE'
    make %{?_smp_mflags}
popd

    pushd build-10
    %cmake ../source \
      -DCMAKE_INSTALL_PREFIX='/usr' \
      -DHIGH_BIT_DEPTH='TRUE' \
      -DEXPORT_C_API='FALSE' \
      -DENABLE_CLI='FALSE' \
      -DENABLE_HDR10_PLUS=YES \
      -DENABLE_SHARED='FALSE'
    make %{?_smp_mflags}
popd

    pushd build-8
    ln -s ../build-10/libx265.a libx265_main10.a
    ln -s ../build-12/libx265.a libx265_main12.a

    %cmake ../source \
      -DCMAKE_INSTALL_PREFIX='/usr' \
      -DENABLE_SHARED='TRUE' \
      -DEXTRA_LIB='x265_main10.a;x265_main12.a' \
      -DEXTRA_LINK_FLAGS='-L.' \
      -DENABLE_HDR10_PLUS=YES \
      -DLINKED_10BIT='TRUE' \
      -DLINKED_12BIT='TRUE'
    make %{?_smp_mflags}
popd


%install

pushd build-8
make DESTDIR=%{buildroot} install
rm %{buildroot}%{_libdir}/libx265.a

%post libs -p /usr/bin/ldconfig
%postun libs -p /usr/bin/ldconfig

%files
/usr/bin/x265

%files libs
/usr/lib64/libx265.so
/usr/lib64/libx265.so.*
/usr/lib64/libhdr10plus.so

%files dev
%doc doc/*
/usr/include/x265.h
/usr/include/x265_config.h
/usr/include/hdr10plus.h
/usr/lib64/libhdr10plus.a
/usr/lib64/pkgconfig/x265.pc


%changelog
# based on https://github.com/UnitedRPMs/x265
