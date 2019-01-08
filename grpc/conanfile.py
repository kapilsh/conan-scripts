import os
import sys

from conans import ConanFile, CMake, tools

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class GRPCConan(ConanFile):
    from gcc import GCC_VERSIONS, CURRENT_GCC_VERSION

    with open(os.path.join(os.path.dirname(os.path.realpath(
            __file__)), "VERSION.txt"), 'r') as version_file:
        version = version_file.read()

    name = "grpc"

    description = "Google Protobuf Serialization Library."
    license = "Apache-2.0"
    requires = (f"gcc/{CURRENT_GCC_VERSION}@kapilsh/release",
                f"protobuf/3.6.1@kapilsh/release",
                f"cares/1.14.0@kapilsh/release",
                f"gflags/2.2.1@kapilsh/release",
                f"google_benchmark/1.4.0@kapilsh/release",
                f"zlib/1.2.11@kapilsh/release",
                f"openssl/1.1.1@kapilsh/release")
    settings = {"os": ["Linux"],
                "compiler": {"gcc": {"version": GCC_VERSIONS}},
                "arch": ["x86_64"],
                "build_type": ["Debug", "Release"]}
    generators = "cmake"
    exports = "VERSION.txt", "../gcc.py"
    short_paths = True
    source_subfolder = "src"
    bulild_policy = "missing"
    url = "https://github.com/grpc/grpc/"

    def source(self):
        tools.get("https://github.com/grpc/grpc/archive/v{}.zip".format(
            self.version))
        os.rename("grpc-{}".format(self.version), self.source_subfolder)

    def build_cmake_prefix_path(self, cmake, *paths):
        cmake.definitions["CMAKE_PREFIX_PATH"] = ";".join(paths)

    def build(self):
        cmake = CMake(self)
        cmake.definitions["gRPC_INSTALL"] = "ON"
        cmake.definitions["gRPC_BUILD_CSHARP_EXT"] = "OFF"
        cmake.definitions["gRPC_BUILD_TESTS"] = "OFF"
        cmake.definitions["gRPC_PROTOBUF_PROVIDER"] = "package"
        cmake.definitions["gRPC_ZLIB_PROVIDER"] = "package"
        cmake.definitions["gRPC_CARES_PROVIDER"] = "package"
        cmake.definitions["gRPC_SSL_PROVIDER"] = "package"
        cmake.definitions["gRPC_GFLAGS_PROVIDER"] = "package"
        cmake.definitions["gRPC_BENCHMARK_PROVIDER"] = "package"
        cmake.definitions["gRPC_BENCHMARK_PROVIDER"] = "package"
        cmake.definitions["CMAKE_INSTALL_PREFIX"] = "install"
        self.output.info(self.deps_cpp_info.rootpaths)

        cmake.definitions["ZLIB_ROOT"] = self.deps_cpp_info[
            "zlib"].rootpath
        cmake.definitions["OPENSSL_ROOT_DIR"] = self.deps_cpp_info[
            "openssl"].rootpath

        self.build_cmake_prefix_path(
            cmake,
            self.deps_cpp_info["cares"].rootpath,
            self.deps_cpp_info["protobuf"].rootpath,
            self.deps_cpp_info["gflags"].rootpath,
            self.deps_cpp_info["google_benchmark"].rootpath)

        cmake.configure(source_folder=self.source_subfolder)
        cmake.build()
        cmake.install()

    def package(self):
        self.copy("*", dst="include", src="install/include")
        self.copy("*.a", dst="lib", src="install/lib")
        self.copy("*", dst="bin", src="install/bin")

    def package_info(self):
        self.cpp_info.libs = [
            "address_sorting",
            "gpr",
            "grpc",
            "grpc_cronet",
            "grpc_plugin_support",
            "grpc_unsecure",
            "grpc++",
            "grpc++_cronet",
            "grpc++_error_details",
            "grpc++_reflection",
            "grpc++_unsecure"]
        self.env_info.LD_LIBRARY_PATH.append("{}/lib".format(
            self.package_folder))
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
        self.cpp_info.includedirs = ['include']
        self.env_info.CPATH.append("{}/include".format(self.package_folder))
