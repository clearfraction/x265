%global gitdate 20191201
%global commit0 b5c86a64bbbede216b25092def72272ecde5523a
%global shortcommit0 %(c=%{commit0}; echo ${c:0:12})  
%global gver .git%{shortcommit0}
%global abi_package %{nil}

Summary: 	H.265/HEVC encoder
Name: 		x265
Group:		Applications/Multimedia
Version: 	3.2.1
Release: 	7%{?dist}
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

%post libs -p /sbin/ldconfig
%postun libs -p /sbin/ldconfig

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

* Sun Dec 01 2019 David Va <davidva AT tuta DOT io> - 3.2.1-7
- Updated to 3.2.1-7

* Fri Aug 02 2019 David Vásquez <davidjeremias82 AT gmail DOT com> - 3.1.2-7
- Updated to 3.1.2-7

* Thu Jul 11 2019 David Vásquez <davidjeremias82 AT gmail DOT com> - 3.1.1-7
- Updated to 3.1.1-7

* Fri Jun 21 2019 David Vásquez <davidjeremias82 AT gmail DOT com> - 3.1-7.git492e3c4
- Updated to 3.1-7.git492e3c4

* Wed Feb 06 2019 David Vásquez <davidjeremias82 AT gmail DOT com> - 3.0-7.git9394080
- Updated to 3.0-7.git9394080

* Wed Oct 10 2018 David Vásquez <davidjeremias82 AT gmail DOT com> - 2.9-7.git975a2e1
- Updated to 2.9-7.git975a2e1

* Tue May 22 2018 David Vásquez <davidjeremias82 AT gmail DOT com> - 2.8-3.gitba0d009
- Updated to 2.8-3.gitba0d009

* Sun Apr 15 2018 David Vásquez <davidjeremias82 AT gmail DOT com> - 2.7-3.git56b216f
- Devel package fix

* Wed Feb 21 2018 David Vásquez <davidjeremias82 AT gmail DOT com> - 2.7-2.git56b216f
- Updated to 2.7-2.git56b216f

* Sat Dec 02 2017 David Vásquez <davidjeremias82 AT gmail DOT com> - 2.6-2.gite293b13
- Updated to 2.6-2.gite293b13

* Mon Oct 02 2017 David Vásquez <davidjeremias82 AT gmail DOT com> - 2.5-3.gitb28e239
- Updated to 2.5-3.gitb28e239

* Tue Sep 26 2017 David Vásquez <davidjeremias82 AT gmail DOT com> - 2.5-2.gite8a6c75
- Updated to 2.5-2.gite8a6c75

* Thu May 25 2017 David Vásquez <davidjeremias82 AT gmail DOT com> - 2.4-2.gitb2d3ae4
- Updated to 2.4-2.gitb2d3ae4

* Mon Apr 17 2017 David Vásquez <davidjeremias82 AT gmail DOT com> - 2.3-2.git97492ac
- Updated to 2.3-2-20170417git97492ac

* Sun Feb 26 2017 David Vásquez <davidjeremias82 AT gmail DOT com> - 2.2-2.git3daed96
- Updated to 2.2-2-20170226git3daed96

* Fri Jul 08 2016 David Vásquez <davidjeremias82 AT gmail DOT com> - 1.9-2.git40ba1eb
- Massive rebuild

* Tue Jul 14 2015 David Vásquez <davidjeremias82 AT gmail DOT com> - 1.9-1.git40ba1eb
- Updated to 1.9-20160221-40ba1eb

* Tue Jul 14 2015 David Vásquez <davidjeremias82 AT gmail DOT com> - 1.7-1
- Updated to 1.7
- Patched detection of ARM
- Added git tag in x265-snapshot.sh
- Thanks to Torsten Gruner and aloisio@gmx.com for tips in build (ARM patches)

* Wed Apr 15 2015 Dominik Mierzejewski <rpm@greysector.net> 1.6-1
- update to 1.6 (ABI bump, rfbz#3593)
- release tarballs are now hosted on videolan.org
- drop obsolete patches

* Thu Dec 18 2014 Dominik Mierzejewski <rpm@greysector.net> 1.2-6
- fix build on armv7l arch (partially fix rfbz#3361, patch by Nicolas Chauvet)
- don't run tests on ARM for now (rfbz#3361)

* Sun Aug 17 2014 Dominik Mierzejewski <rpm@greysector.net> 1.2-5
- don't include contributor agreement in doc
- make sure /usr/share/doc/x265 is owned
- add a comment noting which files are BSD-licenced

* Fri Aug 08 2014 Dominik Mierzejewski <rpm@greysector.net> 1.2-4
- don't create bogus soname (patch by Xavier)

* Thu Jul 17 2014 Dominik Mierzejewski <rpm@greysector.net> 1.2-3
- fix tr call to remove DOS EOL
- build the library with -fPIC on arm and i686, too

* Sun Jul 13 2014 Dominik Mierzejewski <rpm@greysector.net> 1.2-2
- use version in source URL
- update License tag
- fix EOL in drag-uncrustify.bat
- don't link test binaries with shared binary on x86 (segfault)

* Thu Jul 10 2014 Dominik Mierzejewski <rpm@greysector.net> 1.2-1
- initial build
- fix pkgconfig file install location
- link test binaries with shared library
