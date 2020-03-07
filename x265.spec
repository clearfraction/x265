%global gitdate 20191201
%global commit0 b5c86a64bbbede216b25092def72272ecde5523a
%global shortcommit0 %(c=%{commit0}; echo ${c:0:12})  
%global gver .git%{shortcommit0}
%global abi_package %{nil}

Summary: 	H.265/HEVC encoder
Name: 		x265
Group:		Applications/Multimedia
Version: 	3.2.1
Release: 	8%{?dist}
URL: 		http://x265.org/
Source0:	https://bitbucket.org/multicoreware/x265/get/%{commit0}.tar.gz#/%{name}-%{shortcommit0}.tar.gz
Patch:		pkgconfig_fix.patch
License: 	GPLv2+ and BSD
BuildRequires:  cmake
BuildRequires:  gcc
BuildRequires:  nasm
BuildRequires:  pkg-config
BuildRequires:  numactl-dev

%description
The primary objective of x265 is to become the best H.265/HEVC encoder
available anywhere, offering the highest compression efficiency and the
highest performance on a wide variety of hardware platforms.

This package contains the command line encoder.

%package libs
Summary: H.265/HEVC encoder library
Group: Development/Libraries

%description libs
The primary objective of x265 is to become the best H.265/HEVC encoder
available anywhere, offering the highest compression efficiency and the
highest performance on a wide variety of hardware platforms.

This package contains the shared library.

%package dev
Summary: H.265/HEVC encoder library development files
Group: Development/Libraries
Requires: %{name}-libs%{?_isa} = %{version}-%{release}

%description dev
The primary objective of x265 is to become the best H.265/HEVC encoder
available anywhere, offering the highest compression efficiency and the
highest performance on a wide variety of hardware platforms.
This package contains the shared library development files.

%prep
%setup -n multicoreware-%{name}-%{shortcommit0}
%patch -p1
sed -i 's|set(LIB_INSTALL_DIR lib CACHE STRING "Install location of libraries")|set(LIB_INSTALL_DIR lib64 CACHE STRING "Install location of libraries")|g' source/CMakeLists.txt
mkdir -p build-8 build-10 build-12


%build
export http_proxy=http://127.0.0.1:9/
export https_proxy=http://127.0.0.1:9/
export no_proxy=localhost,127.0.0.1,0.0.0.0
export LANG=C.UTF-8
export GCC_IGNORE_WERROR=1
export AR=gcc-ar
export RANLIB=gcc-ranlib
export NM=gcc-nm
export CFLAGS="$CFLAGS -O3 -ffat-lto-objects -flto=4 "
export FCFLAGS="$CFLAGS -O3 -ffat-lto-objects -flto=4 "
export FFLAGS="$CFLAGS -O3 -ffat-lto-objects -flto=4 "
export CXXFLAGS="$CXXFLAGS -O3 -ffat-lto-objects -flto=4 "

pushd build-12
    %cmake ../source \
      -DCMAKE_INSTALL_PREFIX='/usr' \
      -DHIGH_BIT_DEPTH='TRUE' \
      -DMAIN12='TRUE' \
      -DEXPORT_C_API='FALSE' \
      -DENABLE_CLI='FALSE' \
      -DENABLE_SHARED='FALSE'
    make
popd

    pushd build-10
    %cmake ../source \
      -DCMAKE_INSTALL_PREFIX='/usr' \
      -DHIGH_BIT_DEPTH='TRUE' \
      -DEXPORT_C_API='FALSE' \
      -DENABLE_CLI='FALSE' \
      -DENABLE_SHARED='FALSE'
    make
popd

    pushd build-8
    ln -s ../build-10/libx265.a libx265_main10.a
    ln -s ../build-12/libx265.a libx265_main12.a

    %cmake ../source \
      -DCMAKE_INSTALL_PREFIX='/usr' \
      -DENABLE_SHARED='TRUE' \
      -DEXTRA_LIB='x265_main10.a;x265_main12.a' \
      -DEXTRA_LINK_FLAGS='-L.' \
      -DLINKED_10BIT='TRUE' \
      -DLINKED_12BIT='TRUE'
    make
popd


%install

pushd build-8
make DESTDIR=%{buildroot} install
rm %{buildroot}%{_libdir}/libx265.a

%post libs -p /usr/bin/ldconfig
%postun libs -p /usr/bin/ldconfig

%files
%{_bindir}/x265

%files libs
%{_libdir}/libx265.so.*

%files dev
%doc doc/*
%{_includedir}/x265.h
%{_includedir}/x265_config.h
%{_libdir}/libx265.so
%{_libdir}/pkgconfig/x265.pc

%changelog
# based on https://github.com/UnitedRPMs/x265
