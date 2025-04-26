{ stdenv,
  Cocoa,
  CoreGraphics,
  ForceFeedback,
  OpenAL,
  OpenGL,
  SDL,
  addDriverRunpath,
  alembic,
  blender,
  boost,
  brotli,
  callPackage,
  cmake,
  colladaSupport ? true,
  config,
  cudaPackages,
  cudaSupport ? config.cudaSupport,
  dbus,
  embree,
  fetchgit,
  fetchpatch2,
  fetchzip,
  ffmpeg,
  fftw,
  fftwFloat,
  freetype,
  gettext,
  glew,
  gmp,
  hipSupport ? false,
  jackaudioSupport ? false,
  jemalloc,
  lib,
  libGL,
  libGLU,
  libX11,
  libXext,
  libXi,
  libXrender,
  libXxf86vm,
  libdecor,
  libepoxy,
  libffi,
  libharu,
  libjack2,
  libjpeg,
  libpng,
  libsamplerate,
  libsndfile,
  libspnav,
  libtiff,
  libwebp,
  libxkbcommon,
  llvmPackages,
  makeWrapper,
  mesa,
  openal,
  opencollada,
  opencolorio,
  openexr,
  openimagedenoise,
  openimageio,
  openjpeg,
  openpgl,
  opensubdiv,
  openvdb_11,
  openxr-loader,
  pkg-config,
  potrace,
  pugixml,
  python3Packages,
  rocmPackages,
  runCommand,
  spaceNavSupport ? stdenv.hostPlatform.isLinux,
  sse2neon,
  tbb,
  wayland,
  wayland-protocols,
  wayland-scanner,
  waylandSupport ? stdenv.hostPlatform.isLinux,
  zlib,
  zstd,
}
:

let
  embreeSupport =
    (!stdenv.hostPlatform.isAarch64 && stdenv.hostPlatform.isLinux) || stdenv.hostPlatform.isDarwin;
  openImageDenoiseSupport =
    (!stdenv.hostPlatform.isAarch64 && stdenv.hostPlatform.isLinux) || stdenv.hostPlatform.isDarwin;
  openUsdSupport = !stdenv.hostPlatform.isDarwin;

  python3 = python3Packages.python;
  pyPkgsOpenusd = python3Packages.openusd.override { withOsl = false; };

  libdecor' = libdecor.overrideAttrs (old: {
    patches = (old.patches or [ ]) ++ [ ./libdecor.patch ];
  });

  optix = fetchzip {
    url = "https://developer.download.nvidia.com/redist/optix/v7.3/OptiX-7.3.0-Include.zip";
    hash = "sha256-aMrp0Uff4c3ICRn4S6zedf6Q4Mc0/duBhKwKgYgMXVU=";
  };
in

stdenv.mkDerivation (finalAttrs: {
  pname = "vitamix";
  version = "0.1.0";

  srcs = [
    ./.  # Use local source
    (fetchgit {
      name = "assets";
      url = "https://projects.blender.org/blender/blender-assets.git";
      rev = "v${finalAttrs.version}";
      fetchLFS = true;
      hash = "sha256-vepK0inPMuleAJBSipwoI99nMBBiFaK/eSMHDetEtjY=";
    })
  ];

  postUnpack = ''
    chmod -R u+w *
    rm -r assets/working
    mv assets --target-directory source/release/datafiles/
  '';

  sourceRoot = "source";

  patches = [
    ./draco.patch
    (fetchpatch2 {
      url = "https://gitlab.archlinux.org/archlinux/packaging/packages/blender/-/raw/4b6214600e11851d7793256e2f6846a594e6f223/ffmpeg-7-1.patch";
      hash = "sha256-YXXqP/+79y3f41n3cJ3A1RBzgdoYqfKZD/REqmWYdgQ=";
    })
    (fetchpatch2 {
      url = "https://gitlab.archlinux.org/archlinux/packaging/packages/blender/-/raw/4b6214600e11851d7793256e2f6846a594e6f223/ffmpeg-7-2.patch";
      hash = "sha256-mF6IA/dbHdNEkBN5XXCRcLIZ/8kXoirNwq7RDuLRAjw=";
    })
  ] ++ lib.optional stdenv.hostPlatform.isDarwin ./darwin.patch;

  postPatch =
    (lib.optionalString stdenv.hostPlatform.isDarwin ''
      : > build_files/cmake/platform/platform_apple_xcode.cmake
      substituteInPlace source/creator/CMakeLists.txt \
        --replace-fail '${"$"}{LIBDIR}/python' \
                  '${python3}' \
        --replace-fail '${"$"}{LIBDIR}/materialx/' '${python3Packages.materialx}/'
      substituteInPlace build_files/cmake/platform/platform_apple.cmake \
        --replace-fail '${"$"}{LIBDIR}/brotli/lib/libbrotlicommon-static.a' \
                  '${lib.getLib brotli}/lib/libbrotlicommon.dylib' \
        --replace-fail '${"$"}{LIBDIR}/brotli/lib/libbrotlidec-static.a' \
                  '${lib.getLib brotli}/lib/libbrotlidec.dylib'
    '')
    + (lib.optionalString hipSupport ''
      substituteInPlace extern/hipew/src/hipew.c --replace '"/opt/rocm/hip/lib/libamdhip64.so"' '"${rocmPackages.clr}/lib/libamdhip64.so"'
      substituteInPlace extern/hipew/src/hipew.c --replace '"opt/rocm/hip/bin"' '"${rocmPackages.clr}/bin"'
    '');

  env.NIX_CFLAGS_COMPILE = "-I${python3}/include/${python3.libPrefix}";

  cmakeFlags =
    [
      "-DMaterialX_DIR=${python3Packages.materialx}/lib/cmake/MaterialX"
      "-DPYTHON_INCLUDE_DIR=${python3}/include/${python3.libPrefix}"
      "-DPYTHON_LIBPATH=${python3}/lib"
      "-DPYTHON_LIBRARY=${python3.libPrefix}"
      "-DPYTHON_NUMPY_INCLUDE_DIRS=${python3Packages.numpy}/${python3.sitePackages}/numpy/core/include"
      "-DPYTHON_NUMPY_PATH=${python3Packages.numpy}/${python3.sitePackages}"
      "-DPYTHON_VERSION=${python3.pythonVersion}"
      "-DWITH_ALEMBIC=ON"
      "-DWITH_BUILDINFO=OFF"
      "-DWITH_CODEC_FFMPEG=ON"
      "-DWITH_CODEC_SNDFILE=ON"
      "-DWITH_CPU_CHECK=OFF"
      "-DWITH_CYCLES_DEVICE_OPTIX=${if cudaSupport then "ON" else "OFF"}"
      "-DWITH_CYCLES_EMBREE=${if embreeSupport then "ON" else "OFF"}"
      "-DWITH_CYCLES_OSL=OFF"
      "-DWITH_FFTW3=ON"
      "-DWITH_HYDRA=${if openUsdSupport then "ON" else "OFF"}"
      "-DWITH_IMAGE_OPENJPEG=ON"
      "-DWITH_INSTALL_PORTABLE=OFF"
      "-DWITH_JACK=${if jackaudioSupport then "ON" else "OFF"}"
      "-DWITH_LIBS_PRECOMPILED=OFF"
      "-DWITH_MOD_OCEANSIM=ON"
      "-DWITH_OPENCOLLADA=${if colladaSupport then "ON" else "OFF"}"
      "-DWITH_OPENCOLORIO=ON"
      "-DWITH_OPENIMAGEDENOISE=${if openImageDenoiseSupport then "ON" else "OFF"}"
      "-DWITH_OPENSUBDIV=ON"
      "-DWITH_OPENVDB=ON"
      "-DWITH_PULSEAUDIO=OFF"
      "-DWITH_PYTHON_INSTALL=OFF"
      "-DWITH_PYTHON_INSTALL_NUMPY=OFF"
      "-DWITH_PYTHON_INSTALL_REQUESTS=OFF"
      "-DWITH_SDL=OFF"
      "-DWITH_STRICT_BUILD_OPTIONS=ON"
      "-DWITH_TBB=ON"
      "-DWITH_USD=${if openUsdSupport then "ON" else "OFF"}"
      "-DALEMBIC_INCLUDE_DIR=${lib.getDev alembic}/include"
      "-DALEMBIC_LIBRARY=${lib.getLib alembic}/lib/libAlembic${stdenv.hostPlatform.extensions.sharedLibrary}"
    ]
    ++ lib.optionals waylandSupport [
      "-DWITH_GHOST_WAYLAND=ON"
      "-DWITH_GHOST_WAYLAND_DBUS=ON"
      "-DWITH_GHOST_WAYLAND_DYNLOAD=OFF"
      "-DWITH_GHOST_WAYLAND_LIBDECOR=ON"
    ]
    ++ lib.optionals stdenv.hostPlatform.isDarwin [
      "-DLIBDIR=/does-not-exist"
      "-DSSE2NEON_INCLUDE_DIR=${sse2neon}/lib"
    ]
    ++ lib.optional stdenv.cc.isClang "-DPYTHON_LINKFLAGS="
    ++ lib.optionals cudaSupport [
      "-DOPTIX_ROOT_DIR=${optix}"
      "-DWITH_CYCLES_CUDA_BINARIES=ON"
    ];

  preConfigure = ''
    (
      expected_python_version=$(grep -E --only-matching 'set\(_PYTHON_VERSION_SUPPORTED [0-9.]+\)' build_files/cmake/Modules/FindPythonLibsUnix.cmake | grep -E --only-matching '[0-9.]+' )
      actual_python_version=$(python -c 'import sys; print(".".join(map(str, sys.version_info[0:2])))')
      if ! [[ "$actual_python_version" = "$expected_python_version" ]]; then
        echo "wrong Python version, expected '$expected_python_version', got '$actual_python_version'" >&2
        exit 1
      fi
    )
  '';

  nativeBuildInputs =
    [
      cmake
      llvmPackages.llvm.dev
      makeWrapper
      python3Packages.wrapPython
    ]
    ++ lib.optionals cudaSupport [
      addDriverRunpath
      cudaPackages.cuda_nvcc
    ]
    ++ lib.optionals waylandSupport [
      pkg-config
      wayland-scanner
    ];

  buildInputs =
    [
      alembic
      boost
      ffmpeg
      fftw
      fftwFloat
      freetype
      gettext
      glew
      gmp
      jemalloc
      libepoxy
      libharu
      libjpeg
      libpng
      libsamplerate
      libsndfile
      libtiff
      libwebp
      opencolorio
      openexr
      openimageio
      openjpeg
      openpgl
      (opensubdiv.override { inherit cudaSupport; })
      openvdb_11
      potrace
      pugixml
      python3
      python3Packages.materialx
      tbb
      zlib
      zstd
    ]
    ++ lib.optional embreeSupport embree
    ++ lib.optional openImageDenoiseSupport (openimagedenoise.override { inherit cudaSupport; })
    ++ (
      if (!stdenv.hostPlatform.isDarwin) then
        [
          libGL
          libGLU
          libX11
          libXext
          libXi
          libXrender
          libXxf86vm
          openal
          openxr-loader
        ]
      else
        [
          apple-sdk_15
          Cocoa
          CoreGraphics
          ForceFeedback
          OpenAL
          OpenGL
          SDL
          brotli
          llvmPackages.openmp
          sse2neon
        ]
    )
    ++ lib.optionals cudaSupport [ cudaPackages.cuda_cudart ]
    ++ lib.optionals openUsdSupport [ pyPkgsOpenusd ]
    ++ lib.optionals waylandSupport [
      dbus
      libdecor'
      libffi
      libxkbcommon
      wayland
      wayland-protocols
    ]
    ++ lib.optional colladaSupport opencollada
    ++ lib.optional jackaudioSupport libjack2
    ++ lib.optional spaceNavSupport libspnav;

  # Build in build_darwin and copy the app bundle directly
  buildPhase = ''
    cmake -S . -B build_darwin $cmakeFlags
    cmake --build build_darwin -- -j${NIX_BUILD_CORES}
  '';

  installPhase = ''
    runHook preInstall
    mkdir -p $out
    if [ "$(uname)" = "Darwin" ]; then
      cp -a build_darwin/bin/Blender.app $out/
    else
      mkdir -p $out/bin
      cp build_darwin/bin/Blender.app/Contents/MacOS/Blender $out/bin/Blender
    fi
    runHook postInstall
  '';

  postFixup = lib.optionalString cudaSupport ''
    addDriverRunpath $out/bin/Blender
  '';

  passthru = {
    python = python3;
    pythonPackages = python3Packages;

    withPackages =
      f:
      (callPackage ./wrapper.nix { }).override {
        blender = finalAttrs.finalPackage;
        extraModules = (f python3Packages);
      };

    tests = {
      render = runCommand "${finalAttrs.pname}-test" { nativeBuildInputs = [ mesa.llvmpipeHook ]; } ''
        set -euo pipefail
        cat <<'PYTHON' > scene-config.py
        import bpy
        bpy.context.scene.eevee.taa_render_samples = 32
        bpy.context.scene.cycles.samples = 32
        if ${if (stdenv.hostPlatform.isAarch64 && stdenv.hostPlatform.isLinux) then "True" else "False"}:
            bpy.context.scene.cycles.use_denoising = False
        bpy.context.scene.render.resolution_x = 100
        bpy.context.scene.render.resolution_y = 100
        bpy.context.scene.render.threads_mode = 'FIXED'
        bpy.context.scene.render.threads = 1
        PYTHON

        mkdir $out
        for engine in BLENDER_EEVEE_NEXT CYCLES; do
          echo "Rendering with $engine..."
          ${lib.getExe finalAttrs.finalPackage} \
            --background \
            -noaudio \
            --factory-startup \
            --python-exit-code 1 \
            --python scene-config.py \
            --engine "$engine" \
            --render-output "$out/$engine" \
            --render-frame 1
        done
      '';
      tester-cudaAvailable = cudaPackages.writeGpuTestPython { } ''
        import subprocess
        subprocess.run([$${
          lib.concatMapStringsSep ", " (x: ''"${x}"'') [
            (lib.getExe (blender.override { cudaSupport = true; }))
            "--background"
            "-noaudio"
            "--python-exit-code"
            "1"
            "--python"
            "${./test-cuda.py}"
          ]
        }], check=True)  # noqa: E501
      '';
    };
  };

  meta = {
    description = "3D Creation/Animation/Publishing System";
    homepage = "https://www.blender.org";
    license =
      with lib.licenses;
      [ gpl2Plus ] ++ lib.optional cudaSupport (unfree // { shortName = "NVidia OptiX EULA"; });
    platforms = [
      "aarch64-linux"
      "x86_64-darwin"
      "x86_64-linux"
      "aarch64-darwin"
    ];
    broken = stdenv.hostPlatform.isDarwin;
    maintainers = with lib.maintainers; [
      amarshall
      veprbl
    ];
    mainProgram = "blender";
  };
})
