{
  description = "A Nix-flake-based C/C++ development environment";

  inputs.nixpkgs.url = "https://flakehub.com/f/NixOS/nixpkgs/0.1.*.tar.gz";

  outputs = { self, nixpkgs }:
    let
      supportedSystems = [ "x86_64-linux" "aarch64-linux" "x86_64-darwin" "aarch64-darwin" ];
      forEachSupportedSystem = f: nixpkgs.lib.genAttrs supportedSystems (system: f {
        pkgs = import nixpkgs { inherit system; };
      });

      # CMake globals
      globalCMakeFLags = [
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

        # Blender supplies its own FindAlembic.cmake (incompatible with the Alembic-supplied config file)
      "-DALEMBIC_INCLUDE_DIR=${lib.getDev alembic}/include"
      "-DALEMBIC_LIBRARY=${lib.getLib alembic}/lib/libAlembic${stdenv.hostPlatform.extensions.sharedLibrary}"
      ];

      sharedPackages = pkgs: with pkgs; [
        apple-sdk_15
        clang-tools
        cmake
        gtest
      ];
    in
    {
      devShells = forEachSupportedSystem ({ pkgs }: {
        default = pkgs.mkShell {
            packages = sharedPackages pkgs ++ [
              codespell
              conan
              cppcheck
              doxygen
              lcov
              vcpkg
              vcpkg-tool
            ] ++ (if pkgs.stdenv.hostPlatform.system == "aarch64-darwin" then [ ] else [ pkgs.gdb ]);
          };
      });
      packages = forEachSupportedSystem ({ pkgs }: {
        vitamix = pkgs.stdenv.mkDerivation {
          pname = "vitamix";
          version = "0.1.0";
          src = .;

          nativeBuildInputs = [ ];

          cmakeFlags =
            globalCmakeFlags ++
            (if pkgs.stdenv.hostPlatform.system == "aarch64-darwin" then [
              "-DLIBDIR=/does-not-exist"
      "-DSSE2NEON_INCLUDE_DIR=${sse2neon}/lib"
            ] else []);

        }
      }
    };
}