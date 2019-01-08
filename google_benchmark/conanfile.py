import sys
import shutil

from conans import ConanFile, CMake, tools
import os

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class GoogleBenchmarkConan(ConanFile):
    from gcc import GCC_VERSIONS, CURRENT_GCC_VERSION

    with open(os.path.join(os.path.dirname(os.path.realpath(
            __file__)), "VERSION.txt"), 'r') as version_file:
        version = version_file.read()

    name = "google_benchmark"
    requires = f"gcc/{CURRENT_GCC_VERSION}@kapilsh/release"
    description = "Google micro benchmarking tools."
    license = "Apache-2.0"
    settings = {"os": ["Linux"],
                "compiler": {"gcc": {"version": GCC_VERSIONS}},
                "arch": ["x86_64"],
                "build_type": ["Debug", "Release"]}
    generators = "cmake"
    exports = "VERSION.txt", "../gcc.py"
    url = "https://github.com/google/benchmark"

    github_url = "https://github.com/google/benchmark/archive/"

    def source(self):
        zip_file = "v{}.zip".format(self.version)
        tools.download("{}/{}".format(self.github_url, zip_file), zip_file)
        tools.unzip(zip_file)
        os.unlink(zip_file)
        shutil.move("benchmark-{}".format(self.version), "benchmark")

    def build(self):
        cmake = CMake(self)
        cmake.definitions["BENCHMARK_ENABLE_TESTING"] = "OFF"
        cmake.definitions["CMAKE_INSTALL_PREFIX"] = "install"
        cmake.configure(source_folder="benchmark")
        cmake.build()
        cmake.install()

    def package(self):
        self.copy("*", dst="include", src="install/include")
        self.copy("*", dst="lib", src="install/lib")
        self.copy("*", dst="bin", src="install/bin")

    def package_info(self):
        self.cpp_info.libs = ["benchmark"]
        self.env_info.LD_LIBRARY_PATH.append("{}/lib".format(
            self.package_folder))
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
        self.cpp_info.includedirs = ['include']
        self.env_info.CPATH.append("{}/include".format(self.package_folder))
