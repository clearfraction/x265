#
# spec file for package x265
#
# Copyright (c) 2019 Packman Team <packman@links2linux.de>
# Copyright (c) 2014 Torsten Gruner <t.gruner@katodev.de>
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Please submit bugfixes or comments via https://bugs.links2linux.org/
#


%define soname  179
%define libname lib%{name}
%define libsoname %{libname}-%{soname}
Name:           x265
Version:        3.2.1
Release:        1.1
Summary:        A free h265/HEVC encoder - encoder binary
License:        GPL-2.0-or-later
Group:          Productivity/Multimedia/Video/Editors and Convertors
URL:            https://bitbucket.org/multicoreware/x265/wiki/Home
Source0:        https://bitbucket.org/multicoreware/x265/downloads/%{name}_%{version}.tar.gz
Patch1:         x265.pkgconfig.patch
Patch2:         x265-fix_enable512.patch
BuildRequires:  cmake
BuildRequires:  gcc
BuildRequires:  nasm
BuildRequires:  pkg-config
BuildRequires:  numactl-dev

%description
x265 is a free library for encoding next-generation H265/HEVC video
streams.

%package -n %{libsoname}
Summary:        A free H265/HEVC encoder - encoder binary
Group:          Productivity/Multimedia/Video/Editors and Convertors

%description -n %{libsoname}
x265 is a free library for encoding next-generation H265/HEVC video
streams.

%package -n %{libname}-devel
Summary:        Libraries and include file for the %{libname} encoder
Group:          Development/Libraries/C and C++
Requires:       %{buildrequires}
Requires:       %{libsoname} = %{version}
Provides:       %{name}-devel = %{version}
Obsoletes:      %{name}-devel < %{version}

%description -n %{libname}-devel
x265 is a free library for encoding next-generation H265/HEVC video
streams.

%prep
%setup -q -n %{name}_%{version}
%patch1 -p1
%patch2 -p1

sed -i -e "s/0.0/%{soname}.0/g" source/cmake/version.cmake

%build
SOURCE_DIR="$PWD"/source
COMMON_FLAGS="-DENABLE_TESTS=OFF -DENABLE_PIC=ON"
HIGH_BIT_DEPTH_FLAGS="-DENABLE_CLI=OFF -DENABLE_SHARED=OFF -DEXPORT_C_API=OFF -DHIGH_BIT_DEPTH=ON"

%define __sourcedir ./source

# Build 10bit depth version of the library
%define __builddir ./source/build-10bit
%cmake $COMMON_FLAGS $HIGH_BIT_DEPTH_FLAGS \

make %{?_smp_mflags}
cd ../..

# Build 12bit depth version of the library
%define __builddir ./source/build-12bit
%cmake $COMMON_FLAGS $HIGH_BIT_DEPTH_FLAGS -DMAIN12=ON \


make %{?_smp_mflags}
cd ../..

mv source/build-10bit/libx265.a source/build-10bit/libx265_main10.a
mv source/build-12bit/libx265.a source/build-12bit/libx265_main12.a

# Build general version of the library linking in the 10/12bit depth versions
%define __builddir ./source/build
%cmake -DENABLE_TESTS=OFF \
       -DENABLE_PIC=ON \
       -DENABLE_CLI=ON \
       -DLINKED_10BIT=ON \
       -DLINKED_12BIT=ON \
       -DEXTRA_LINK_FLAGS="-L$SOURCE_DIR/build-10bit -L$SOURCE_DIR/build-12bit" \
       -DEXTRA_LIB="x265_main10.a;x265_main12.a"

cd source
%cmake $COMMON_FLAGS
%endif
make %{?_smp_mflags}
cd ../../

%install
%cmake_install
rm -f %{buildroot}%{_libdir}/%{libname}.a
echo "%{libname}-%{soname}" > %{_sourcedir}/baselibs.conf

%post -n %{libsoname} -p /sbin/ldconfig
%postun -n %{libsoname} -p /sbin/ldconfig

%files -n %{libsoname}
%{_libdir}/%{libname}.so.%{soname}*

%files
%{_bindir}/%{name}

%files -n %{libname}-devel
%license COPYING
%doc readme.rst
%{_includedir}/%{name}.h
%{_includedir}/%{name}_config.h
%{_libdir}/pkgconfig/%{name}.pc
%{_libdir}/%{libname}.so

%changelog
* Sun Dec  1 2019 Luigi Baldoni <aloisio@gmx.com>
- Update to version 3.2.1
  * Fix output change in analysis load
  * Fix encoder crash with zones and add test for zones
  * Fix: Performance drop in aq-mode 4 This patch moves the
    memory handling part of the edge information required for
    aq-mode 4 to the Frame class-level in that way it can be
    reused by the threads.
  * Fix: Performance drop in aq-mode 4 This patch moves the
    memory handling part of the edge information required for
    aq-mode 4 to the Frame class-level in that way it can be
    reused by the threads.
  * Fix output change observed during analysis-load for
    inter-refine levels 2 and 3.
  * Adaptive Frame duplication This patch does the following. 1.
    Replaces 2-3 near-identical frames with one frame and sets
    pic_struct based on frame doubling / tripling. 2. Add option
    "--frame-dup" and "--dup-threshold' to enable frame
    duplication and to set threshold for frame similarity
    (optional).
  * Fix: AQ mode 4 commit (21db162) introduces slowdown even is
    not used AQ mode 4.
* Tue Oct  1 2019 enzokiel@kabelmail.de
- Update to version 3.2
  New features
  * 3-level hierarchical motion estimation using --hme and
  - -hme-search.
  * New AQ mode (--aq-mode 4) with variance and edge information.
  * selective-sao to selectively enable SAO at slice level.
  Enhancements to existing features
  * New implementation of --refine-mv with 3 refinement levels.
  Encoder enhancements
  * Improved quality in the frames following dark scenes in ABR
    mode.
  API changes
  * Additions to x265_param structure to support the newly added
    features --hme, --hme-search and selective-sao.
  Bug fixes
  * Fixed encoder crash with --zonefile during failures in
    encoder_open().
  * Fixed JSON11 build errors with HDR10+ on MacOS high sierra.
  * Signalling out of range scaling list data fixed.
  * Inconsistent output fix for 2-pass rate-control with cutree ON.
  Known issues
  * Build dependency on changeset cf37911 of SVT-HEVC.
* Sun Aug 11 2019 Luigi Baldoni <aloisio@gmx.com>
- Update to version 3.1.2
  * No changelog available
- Spec cleanup
* Thu Jul 18 2019 enzokiel@kabelmail.de
- Update to version 3.1.1
  - No changelog available.
- Version 3.1
  New features
  * x265 can invoke SVT-HEVC library for encoding through --svt.
  * x265 can now accept interlaced inputs directly (no need to
    separate fields), and sends it to the encoder with proper fps
    and frame-size through --field.
  * --fades can detect and handle fade-in regions. This option will
    force I-slice and initialize RC history for the brightest frame
    after fade-in.
  API changes
  * A new flag to signal MasterDisplayParams and maxCll/Fall
    separately
  Encoder enhancements
  * Improved the performance of inter-refine level 1 by skipping
    the evaluation of smaller CUs when the current block is decided
    as “skip” by the save mode.
  * New AVX2 primitives to improve the performance of encodes that
    enable --ssim-rd.
  * Improved performance in medium preset with negligible loss in
  quality.
  Bug fixes
  * Bug fixes for zones.
  * Fixed wrap-around from MV structure overflow occurred around 8K
  pixels or over.
  * Fixed issues in configuring cbQpOffset and crQpOffset for 444
    input
  * Fixed cutree offset computation in 2nd pass encodes.
  Known issues
  * AVX512 main12 asm disabling.
  * Inconsistent output with 2-pass due to cutree offset sharing.
* Fri Feb  1 2019 antonio.larrosa@gmail.com
- Support 10 and 12 bit color depths
- Update to version 3.0
  New features
  * option:: '--dolby-vision-profile <integer|float>' generates
    bitstreams confirming to the specified Dolby Vision profile.
    Currently profile 5, profile 8.1 and profile 8.2 enabled,
    Default 0 (disabled)
  * option:: '--dolby-vision-rpu' File containing Dolby Vision RPU
    metadata. If given, x265's Dolby Vision metadata parser will
    fill the RPU field of input pictures with the metadata read
    from the file. The library will interleave access units with
    RPUs in the bitstream. Default NULL (disabled).
  * option:: '--zonefile <filename>' specifies a text file which
    contains the boundaries of the zones where each of zones are
    configurable.
  * option:: '--qp-adaptation-range' Delta-QP range by QP
    adaptation based on a psycho-visual model. Default 1.0.
  * option:: '--refine-ctu-distortion <0/1>' store/normalize ctu
    distortion in analysis-save/load. Default 0.
  * Experimental feature option:: '--hevc-aq' enables adaptive
    quantization. It scales the quantization step size according
    to the spatial activity of one coding unit relative to frame
    average spatial activity. This AQ method utilizes the minimum
    variance of sub-unit in each coding unit to represent the
    coding unit's spatial complexity.
  Encoder enhancements
  * Preset: change param defaults for veryslow and slower preset.
    Replace slower preset with defaults used in veryslow preset
    and change param defaults in veryslow preset as per
    experimental results.
  * AQ: change default AQ mode to auto-variance
  * Cutree offset reuse: restricted to analysis reuse-level 10 for
    analysis-save -> analysis-load
  * Tune: introduce --tune animation option which improves encode
    quality for animated content
  * Reuse CU depth for B frame and allow I, P frame to follow
    x265 depth decision
  Bug fixes
  * RC: fix rowStat computation in const-vbv
  * Dynamic-refine: fix memory reset size.
  * Fix linking issue on non x86 platform
  * Encoder: Do not include CLL SEI message if empty
  * Fix build error in VMAF lib
- Rebase x265-fix_enable512.patch
* Tue Oct  9 2018 aloisio@gmx.com
- Update to version 2.9
  New features:
  * Support for chunked encoding
    + :option:`--chunk-start and --chunk-end`
    + Frames preceding first frame of chunk in display order
    will be encoded, however, they will be discarded in the
    bitstream.
    + Frames following last frame of the chunk in display order
    will be used in taking lookahead decisions, but, they will
    not be encoded.
    + This feature can be enabled only in closed GOP structures.
    Default disabled.
  * Support for HDR10+ version 1 SEI messages.
  Encoder enhancements:
  * Create API function for allocating and freeing
    x265_analysis_data.
  * CEA 608/708 support: Read SEI messages from text file and
    encode it using userSEI message.
  Bug fixes:
  * Disable noise reduction when vbv is enabled.
  * Support minLuma and maxLuma values changed by the
    commandline.
  version 2.8
  New features:
  * :option:`--asm avx512` used to enable AVX-512 in x265.
    Default disabled.
    + For 4K main10 high-quality encoding, we are seeing good
    gains; for other resolutions and presets, we don't
    recommend using this setting for now.
  * :option:`--dynamic-refine` dynamically switches between
    different inter refine levels. Default disabled.
    + It is recommended to use :option:`--refine-intra 4' with
    dynamic refinement for a better trade-off between encode
    efficiency and performance than using static refinement.
  * :option:`--single-sei`
    + Encode SEI messages in a single NAL unit instead of
    multiple NAL units. Default disabled.
  * :option:`--max-ausize-factor` controls the maximum AU size
    defined in HEVC specification.
    + It represents the percentage of maximum AU size used.
    Default is 1.
  * VMAF (Video Multi-Method Assessment Fusion)
    + Added VMAF support for objective quality measurement of a
    video sequence.
    + Enable cmake option ENABLE_LIBVMAF to report per frame and
    aggregate VMAF score. The frame level VMAF score does not
    include temporal scores.
    + This is supported only on linux for now.
  Encoder enhancements:
  * Introduced refine-intra level 4 to improve quality.
  * Support for HLG-graded content and pic_struct in SEI message.
  Bug Fixes:
  * Fix 32 bit build error (using CMAKE GUI) in Linux.
  * Fix 32 bit build error for asm primitives.
  * Fix build error on mac OS.
  * Fix VBV Lookahead in analysis load to achieve target bitrate.
- Added x265-fix_enable512.patch
* Fri May  4 2018 zaitor@opensuse.org
- Build with nasm >= 2.13 for openSUSE Leap 42.3 and SLE-12, since
  new enough nasm is now available for them.
* Thu Mar  1 2018 zaitor@opensuse.org
- Update to version 2.7:
  * New features:
  - option:`--gop-lookahead` can be used to extend the gop
    boundary(set by `--keyint`). The GOP will be extended, if a
    scene-cut frame is found within this many number of frames.
  - Support for RADL pictures added in x265.
  - option:`--radl` can be used to decide number of RADL pictures
    preceding the IDR picture.
  * Encoder enhancements:
  - Moved from YASM to NASM assembler. Supports NASM assembler
    version 2.13 and greater.
  - Enable analysis save and load in a single run. Introduces two
    new cli options `--analysis-save <filename>` and
    `--analysis-load <filename>`.
  - Comply to HDR10+ LLC specification.
  - Reduced x265 build time by more than 50%% by re-factoring
    ipfilter.asm.
  * Bug fixes:
  - Fixed inconsistent output issue in deblock filter and
  - -const-vbv.
  - Fixed Mac OS build warnings.
  - Fixed inconsistency in pass-2 when weightp and cutree are
    enabled.
  - Fixed deadlock issue due to dropping of BREF frames, while
    forcing slice types through qp file.
- Bump soname to 151, also in baselibs.conf following upstream
  changes.
- Replace yasm with nasm BuildRequires following upstreams changes.
* Fri Dec  1 2017 joerg.lorenzen@ki.tng.de
- Update to version 2.6
  New features
  * x265 can now refine analysis from a previous HEVC encode (using
    options --refine-inter, and --refine-intra), or a previous AVC
    encode (using option --refine-mv-type). The previous encode’s
    information can be packaged using the x265_analysis_data_t data
    field available in the x265_picture object.
  * Basic support for segmented (or chunked) encoding added with
  - -vbv-end that can specify the status of CPB at the end of a
    segment. String this together with --vbv-init to encode a title
    as chunks while maintaining VBV compliance!
  * --force-flush can be used to trigger a premature flush of the
    encoder. This option is beneficial when input is known to be
    bursty, and may be at a rate slower than the encoder.
  * Experimental feature --lowpass-dct that uses truncated DCT for
    transformation.
  Encoder enhancements
  * Slice-parallel mode gets a significant boost in performance,
    particularly in low-latency mode.
  * x265 now officially supported on VS2017.
  * x265 now supports all depths from mono0 to mono16 for Y4M
    format.
  API changes
  * Options that modified PPS dynamically (--opt-qp-pps and
  - -opt-ref-list-length-pps) are now disabled by default to
    enable users to save bits by not sending headers. If these
    options are enabled, headers have to be repeated for every GOP.
  * Rate-control and analysis parameters can dynamically be
    reconfigured simultaneously via the x265_encoder_reconfig API.
  * New API functions to extract intermediate information such as
    slice-type, scenecut information, reference frames, etc. are
    now available. This information may be beneficial to
    integrating applications that are attempting to perform
    content-adaptive encoding. Refer to documentation on
    x265_get_slicetype_poc_and_scenecut, and
    x265_get_ref_frame_list for more details and suggested usage.
  * A new API to pass supplemental CTU information to x265 to
    influence analysis decisions has been added. Refer to
    documentation on x265_encoder_ctu_info for more details.
  Bug fixes
  * Bug fixes when --slices is used with VBV settings.
  * Minor memory leak fixed for HDR10+ builds, and default x265
    when pools option is specified.
  * HDR10+ bug fix to remove dependence on poc counter to select
    meta-data information.
* Thu Jul 27 2017 joerg.lorenzen@ki.tng.de
- Update to version 2.5
  Encoder enhancements
  * Improved grain handling with --tune grain option by throttling
    VBV operations to limit QP jumps.
  * Frame threads are now decided based on number of threads
    specified in the --pools, as opposed to the number of hardware
    threads available. The mapping was also adjusted to improve
    quality of the encodes with minimal impact to performance.
  * CSV logging feature (enabled by --csv) is now part of the
    library; it was previously part of the x265 application.
    Applications that integrate libx265 can now extract frame level
    statistics for their encodes by exercising this option in the
    library.
  * Globals that track min and max CU sizes, number of slices, and
    other parameters have now been moved into instance-specific
    variables. Consequently, applications that invoke multiple
    instances of x265 library are no longer restricted to use the
    same settings for these parameter options across the multiple
    instances.
  * x265 can now generate a seprate library that exports the HDR10+
    parsing API. Other libraries that wish to use this API may do
    so by linking against this library. Enable ENABLE_HDR10_PLUS in
    CMake options and build to generate this library.
  * SEA motion search receives a 10%% performance boost from AVX2
    optimization of its kernels.
  * The CSV log is now more elaborate with additional fields such
    as PU statistics, average-min-max luma and chroma values, etc.
    Refer to documentation of --csv for details of all fields.
  * x86inc.asm cleaned-up for improved instruction handling.
  API changes
  * New API x265_encoder_ctu_info() introduced to specify suggested
    partition sizes for various CTUs in a frame. To be used in
    conjunction with --ctu-info to react to the specified
    partitions appropriately.
  * Rate-control statistics passed through the x265_picture object
    for an incoming frame are now used by the encoder.
  * Options to scale, reuse, and refine analysis for incoming
    analysis shared through the x265_analysis_data field in
    x265_picture for runs that use --analysis-reuse-mode load; use
    options --scale, --refine-mv, --refine-inter, and
  - -refine-intra to explore.
  * VBV now has a deterministic mode. Use --const-vbv to exercise.
  Bug fixes
  * Several fixes for HDR10+ parsing code including incompatibility
    with user-specific SEI, removal of warnings, linking issues in
    linux, etc.
  * SEI messages for HDR10 repeated every keyint when HDR options
    (--hdr-opt, --master-display) specified.
- soname bump to 130.
* Thu Apr 27 2017 joerg.lorenzen@ki.tng.de
- Update to version 2.4
  Encoder enhancements
  * HDR10+ supported. Dynamic metadata may be either supplied as a
    bitstream via the userSEI field of x265_picture, or as a json
    jile that can be parsed by x265 and inserted into the bitstream;
    use --dhdr10-info to specify json file name, and --dhdr10-opt
    to enable optimization of inserting tone-map information only
    at IDR frames, or when the tone map information changes.
  * Lambda tables for 8, 10, and 12-bit encoding revised, resulting
    in significant enhancement to subjective visual quality.
  * Enhanced HDR10 encoding with HDR-specific QP optimzations for
    chroma, and luma planes of WCG content enabled; use --hdr-opt
    to activate.
  * Ability to accept analysis information from other previous
    encodes (that may or may not be x265), and selectively reuse
    and refine analysis for encoding subsequent passes enabled with
    the --refine-level option.
  * Slow and veryslow presets receive a 20%% speed boost at
    iso-quality by enabling the --limit-tu option.
  * The bitrate target for x265 can now be dynamically reconfigured
    via the reconfigure API.
  * Performance optimized SAO algorithm introduced via the
  - -limit-sao option; seeing 10%% speed benefits at faster presets.
  API changes
  * x265_reconfigure API now also accepts rate-control parameters
    for dynamic reconfiguration.
  * Several additions to data fields in x265_analysis to support
  - -refine-level: see x265.h for more details.
  Bug fixes
  * Avoid negative offsets in x265 lambda2 table with SAO enabled.
  * Fix mingw32 build error.
  * Seek now enabled for pipe input, in addition to file-based input.
  * Fix issue of statically linking core-utils not working in linux.
  * Fix visual artifacts with --multi-pass-opt-distortion with VBV.
  * Fix bufferFill stats reported in csv.
- soname bump to 116.
* Fri Feb 24 2017 ismail@i10z.com
- Update to version 2.3
  Encoder enhancements
  * New SSIM-based RD-cost computation for improved visual quality,
    and efficiency; use --ssim-rd to exercise.
  * Multi-pass encoding can now share analysis information from
    prior passes.
  * A dedicated thread pool for lookahead can now be specified
    with --lookahead-threads.
  * option:–dynamic-rd dynamically increase analysis in areas
    where the bitrate is being capped by VBV; works for both
    CRF and ABR encodes with VBV settings.
  * The number of bits used to signal the delta-QP can be
    optimized with the --opt-cu-delta-qp option.
  * Experimental feature option:–aq-motion adds new QP offsets
    based on relative motion of a block with respect to the
    movement of the frame.
  API changes
  * Reconfigure API now supports signalling new scaling lists.
  * x265 application’s csv functionality now reports time
    (in milliseconds) taken to encode each frame.
  * --strict-cbr enables stricter bitrate adherence by adding
    filler bits when achieved bitrate is lower than the target.
  * --hdr can be used to ensure that max-cll and max-fall values
    are always signaled (even if 0,0).
  Bug fixes
  * Fixed scaling lists support for 4:4:4 videos.
  * Inconsistent output fix for --opt-qp-pss by removing last
    slice’s QP from cost calculation.
* Sun Jan  1 2017 ismail@i10z.com
-  Update to version 2.2
  Encoder enhancements
  * Enhancements to TU selection algorithm with early-outs for
    improved speed; use --limit-tu to exercise.
  * New motion search method SEA (Successive Elimination Algorithm)
    supported now as :option: –me 4
  * Bit-stream optimizations to improve fields in PPS and SPS for
    bit-rate savings through --[no-]opt-qp-pps,
  - -[no-]opt-ref-list-length-pps, and --[no-]multi-pass-opt-rps.
  * Enabled using VBV constraints when encoding without WPP.
  * All param options dumped in SEI packet in bitstream when info
    selected.
  API changes
  * Options to disable SEI and optional-VUI messages from bitstream
    made more descriptive.
  * New option --scenecut-bias to enable controlling bias to mark
    scene-cuts via cli.
  * Support mono and mono16 color spaces for y4m input.
  * --min-cu-size of 64 no-longer supported for reasons of
    visual quality.
  * API for CSV now expects version string for better integration
    of x265 into other applications.
  Bug fixes
  * Several fixes to slice-based encoding.
  * --log2-max-poc-lsb‘s range limited according to HEVC spec.
  * Restrict MVs to within legal boundaries when encoding.
* Thu Dec 22 2016 scarabeus@opensuse.org
- Add conditional for the numa-devel again it was not ment to be dropped
- Add patch x265.pkgconfig.patch to fix pkgconfig
* Tue Dec 20 2016 scarabeus@opensuse.org
- Switch to use cmake macros
* Thu Sep 29 2016 ismail@i10z.com
- Update to version 2.1
  Encoder enhancements
  * Support for qg-size of 8
  * Support for inserting non-IDR I-frames at scenecuts and when
    running with settings for fixed-GOP (min-keyint = max-keyint)
  * Experimental support for slice-parallelism.
  API changes
  * Encode user-define SEI messages passed in through x265_picture
    object.
  * Disable SEI and VUI messages from the bitstream
  * Specify qpmin and qpmax
  * Control number of bits to encode POC.
  Bug fixes
  * QP fluctuation fix for first B-frame in mini-GOP for 2-pass
    encoding with tune-grain.
  * Assembly fix for crashes in 32-bit from dct_sse4.
  * Threadpool creation fix in windows platform.
* Sun Aug 28 2016 joerg.lorenzen@ki.tng.de
- Update to version 2.0
  API and Key Behavior Changes
  * x265_rc_stats added to x265_picture, containing all RC decision
    points for that frame.
  * PTL: high tier is now allowed by default, chosen only if
    necessary.
  * multi-pass: First pass now uses slow-firstpass by default,
    enabling better RC decisions in future passes.
  * pools: fix behaviour on multi-socketed Windows systems, provide
    more flexibility in determining thread and pool counts.
  * ABR: improve bits allocation in the first few frames, abr reset,
    vbv and cutree improved.
  New Features
  * uhd-bd: Enforce Ultra-HD Blu-ray Disc parameters
    (overrides any other settings).
  * rskip: Enables skipping recursion to analyze lower CU sizes
    using heuristics at different rd-levels. Provides good visual
    quality gains at the highest quality presets.
  * rc-grain: Enables a new rate control mode specifically for
    grainy content. Strictly prevents QP oscillations within and
    between frames to avoid grain fluctuations.
  * tune grain: A fully refactored and improved option to encode
    film grain content including QP control as well as analysis
    options.
  * asm: ARM assembly is now enabled by default, native or cross
    compiled builds supported on armv6 and later systems.
  Misc
  * An SSIM calculation bug was corrected
- soname bump to 87.
- Fixed arm.patch.
- Added libnuma-devel as buildrequires for arch x86_64 (except
  for openSUSE 13.1 because libnuma-devel >= 2.0.9 is required).
* Wed Feb  3 2016 ismail@i10z.com
- Update to version 1.9
  API Changes:
  * x265_frame_stats returns many additional fields: maxCLL, maxFALL,
    residual energy, scenecut and latency logging
  * --qpfile now supports frametype 'K"
  * x265 now allows CRF ratecontrol in pass N (N greater than or equal to 2)
  * Chroma subsampling format YUV 4:0:0 is now fully supported and tested
  New Features:
  * Quant offsets: This feature allows block level quantization offsets
    to be specified for every frame. An API-only feature.
  * --intra-refresh: Keyframes can be replaced by a moving column
    of intra blocks in non-keyframes.
  * --limit-modes: Intelligently restricts mode analysis.
  * --max-luma and --min-luma for luma clipping, optional for HDR use-cases
  * Emergency denoising is now enabled by default in very low bitrate,
    VBV encodes
  Presets and Performance:
  * Recently added features lookahead-slices, limit-modes, limit-refs
    have been enabled by default for applicable presets.
  * The default psy-rd strength has been increased to 2.0
  * Multi-socket machines now use a single pool of threads that can
    work cross-socket.
* Fri Nov 27 2015 aloisio@gmx.com
- Update to version 1.8:
  API Changes:
  * Experimental support for Main12 is now enabled. Partial
    assembly support exists.
  * Main12 and Intra/Still picture profiles are now supported.
    Still picture profile is detected based on
    x265_param::totalFrames.
  * Three classes of encoding statistics are now available
    through the API.
    + x265_stats - contains encoding statistics, available
    through x265_encoder_get_stats()
    + x265_frame_stats and x265_cu_stats - contains frame
    encoding statistics, available through recon x265_picture
  * --csv
  * x265_encoder_log() is now deprecated
  * x265_param::csvfn is also deprecated
  * --log-level now controls only console logging, frame
    level console logging has been removed.
  * Support added for new color transfer characteristic ARIB
    STD-B67
  New Features:
  * limit-refs
    + This feature limits the references analysed for
    individual CUS.
    + Provides a nice tradeoff between efficiency and
    performance.
    + aq-mode 3
  * A new aq-mode that provides additional biasing for
    low-light conditions.
  * An improved scene cut detection logic that allows
    ratecontrol to manage visual quality at fade-ins and
    fade-outs better.
  Preset and Tune Options:
  * tune grain
    + Increases psyRdoq strength to 10.0, and rdoq-level to 2.
    + qg-size
  * Default value changed to 32.
- soname bump to 68
- Reworked arm.patch for 1.8
* Fri May 29 2015 aloisio@gmx.com
- soname bump to 59
- Update to version 1.7
  * large amount of assembly code optimizations
  * some preliminary support for high dynamic range content
  * improvements for multi-library support
  * some new quality features
    (full documentation at: http://x265.readthedocs.org/en/1.7)
  * This release simplifies the multi-library support introduced
    in version 1.6. Any libx265 can now forward API requests to
    other installed libx265 libraries (by name) so applications
    like ffmpeg and the x265 CLI can select between 8bit and 10bit
    encodes at runtime without the need of a shim library or
    library load path hacks. See --output-depth, and
    http://x265.readthedocs.org/en/1.7/api.html#multi-library-interface
  * For quality, x265 now allows you to configure the quantization
    group size smaller than the CTU size (for finer grained AQ
    adjustments). See --qg-size.
  * x265 now supports limited mid-encode reconfigure via a new public
    method: x265_encoder_reconfig()
  * For HDR, x265 now supports signaling the SMPTE 2084 color transfer
    function, the SMPTE 2086 mastering display color primaries, and the
    content light levels. See --master-display, --max-cll
  * x265 will no longer emit any non-conformant bitstreams unless
  - -allow-non-conformance is specified.
  * The x265 CLI now supports a simple encode preview feature. See
  - -recon-y4m-exec.
  * The AnnexB NAL headers can now be configured off, via x265_param.bAnnexB
    This is not configurable via the CLI because it is a function of the
    muxer being used, and the CLI only supports raw output files. See
  - -annexb
  Misc:
  * --lossless encodes are now signaled as level 8.5
  * --profile now has a -P short option
  * The regression scripts used by x265 are now public, and can be found at:
    https://bitbucket.org/sborho/test-harness
  * x265's cmake scripts now support PGO builds, the test-harness can be
    used to drive the profile-guided build process.
* Tue Apr 28 2015 aloisio@gmx.com
- soname bumped to 51
- Update to stable version 1.6
  Perfomance changes:
  * heavy improvements for AVX2 capable platforms
    (Haswell and later Intel CPUs) and work efficiency
    improvements for multiple-socket machines.
  API changes:
  * --threads N replaced by --pools N,N and --lookahead-slices N
  * --[no-]rdoq-level N - finer control over RDOQ effort
  * --min-cu-size N - trade-off compression for performance
  * --max-tu-size N - trade-off compression for performance
  * --[no-]temporal-layers - code unreferenced B frames in temporal
    layer 1
  * --[no-]cip aliases added for --[no-]constrained-intra
  * Added support for new color transfer functions "smpte-st-2084"
    and "smpte-st-428
  * --limit-refs N was added, but not yet implemented
  * Deprecated x265_setup_primitives() was removed from the public
    API and is no longer exported DLLs
  Threading changes:
  * The x265 thread pool has been made NUMA aware.
  * The --threads  parameter, which used to specify a global
    pool size, has been replaced with a --pools parameter which
    allows you to specify a pool size per NUMA node (aka CPU socket
    or package). The default is still to allocate one pool worker
    thread per logical core on the machine, but with --pools one
    can isolate those threads to a given socket.
  * Other than socket isolation, the biggest visible change in the
    NUMA aware thread pools is the increase in work efficiency.
    The total utilization will generally decrease but the performance
    will increase since worker threads spend less time context
    switching.  Also, the threading of the lookahead was made more
    work-efficient. Each lookahead job is a much larger piece of work.
    Before (1.5):
    disable thread pool: --threads 1
    default thread pool: --threads 0
    restrict to 4 threads: --threads 4
    After (1.6):
    disable thread pools: --pools 0
    default thread pools: --pools *
    restrict to 4 threads: --pools 4
    restrict to 4 threads on socket 1: --pools -,4
    restrict to all threads on socket 0: --pools +,-
  Multi-lib interface:
  * In order to support runtime selection of a libx265
    shared library, we have introduced an x265_api structure
    and an x265_api_get() function. Applications which use
    this interface to acquire the libx265 functional interface
    will be able to use shim libraries to bind a particular build
    of libx265 at run time. See the API documentation for full
    details.
* Sun Feb 22 2015 aloisio@gmx.com
- soname bump
- Update to stable version 1.5
  * improvements in Main10 compression efficiency and performance
    and psycho-visual optimizations now enabled by default
  Feature additions:
  * analysis re-use features have been completed
  * rate control zones have been introduced
  * --tune grain introduced
  * deblocking tC and Beta offsets are now configurable
  * denoise is seperately configurable for inter and intra CUs
  * frame based CSV logging has been improved
  * New support for VTune task profiles
  Presets and defaults:
  * ultrafast no longer disables the deblocking loop filter
  * psy-rd defaults to 0.3   (was 0, disabled)
  * psy-rdoq defaults to 1.0 (was 0, disabled)
  * aq-mode defaults to 1    (was 2, auto-variance)
  * 4:2:2 and 4:4:4 encodes no longer generate compliance warnings
  API changes:
  * param.rc.rateTolerance has been removed and replaced with a simpler
    param.rc.bStrictCbr flag.
  * --log-level debug is now --log-level 4 instead of --log-level 3.
    A new 'frame' log level was inserted at level 3 in order to support
    frame level CSV logging without also enabling frame level console
    logging. Using the string name 'debug' is unambiguous as its
    behavior has not changed.
- version 1.4
  * large refactoring in the analysis code
  Feature additions:
  * --pmode (parallel mode decision)
  * --pme (parallel motion estimation).
  Presets and defaults:
  * --amp is now respected in RD levels 2, 3, and 4 (previously only
    in 5 and 6).
  * --b-intra is now respected in all RD levels.
  * --fast-cbf, which has only ever effective at RD levels 5 and 6,
    is no longer enabled uselessly in the fastest presets.
  * --weightb is now enabled by default at presets slower, veryslow,
    and placebo.
  * --cu-lossless was changed to only attempt a lossless encode of
    the best lossy encode method. This made --cu-lossless a much less
    expensive encode option to have enabled, and hopefully made the
    feature more robust and maintainable.
  * The upper threshold for --psy-rdoq was raised to 50 (from 10)
    since the higher values were found to be beneficial for sources
    with high frequency noise (film grain).
  * The default thread pool size logic was updated to account for the
    addition of --pmode and --pme (if WPP is disabled but --pmode or
  - -pme are enabled, a thread pool is still allocated).
* Mon Dec  8 2014 crrodriguez@opensuse.org
- Ensure we use the proper CXXFLAGS, CFLAGS and therefore
  debuginfo packages are generated correctly.
* Sat Oct  4 2014 aloisio@gmx.com
- Bumped to version hg20140928
* Thu Jun  5 2014 guillaume@opensuse.org
- Fix ARM build with arm.patch from Arch Linux:
  https://github.com/archlinuxarm/PKGBUILDs/blob/master/extra/x265/arm.patch
* Thu May  8 2014 Manfred.Tremmel@iiv.de
- added baselibs.conf
* Mon Mar 24 2014 Manfred.Tremmel@iiv.de
- initial build of todays mercurial checkout
