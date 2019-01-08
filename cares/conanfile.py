import os
import shutil

from conans import ConanFile, CMake, tools
from future.moves import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class CAresConan(ConanFile):
    from gcc import GCC_VERSIONS, CURRENT_GCC_VERSION

    with open(os.path.join(os.path.dirname(os.path.realpath(
            __file__)), "VERSION.txt"), 'r') as version_file:
        version = version_file.read()

    requires = "gcc/{}@kapilsh/release".format(CURRENT_GCC_VERSION)
    name = "cares"
    license = "MIT"
    url = "https://github.com/conan-community/conan-cares"
    description = "A C library for asynchronous DNS requests"
    homepage = "https://cares.haxx.se/"
    settings = {"os": ["Linux"],
                "compiler": {"gcc": {"version": GCC_VERSIONS}},
                "arch": ["x86_64"],
                "build_type": ["Debug", "Release"]}
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = "shared=False", "fPIC=True"
    exports = "VERSION.txt", "../gcc.py"
    generators = "cmake"
    source_url = "https://github.com/c-ares/c-ares/archive"

    def source(self):
        ver = self.version.replace(".", "_")
        tar_file = f"cares-{ver}.tar.gz"
        tools.download("{}/{}".format(self.source_url, tar_file), tar_file)
        tools.unzip(tar_file)
        os.unlink(tar_file)
        self.output.info(os.listdir("."))
        shutil.move(f"c-ares-cares-{ver}", "cares")

    def cmake_configure(self):
        cmake = CMake(self)
        cmake.definitions["CMAKE_BUILD_TYPE"] = self.settings.build_type
        cmake.definitions["CARES_STATIC"] = not self.options.shared
        cmake.definitions["CARES_SHARED"] = self.options.shared
        cmake.definitions["CARES_BUILD_TESTS"] = "OFF"
        cmake.configure(source_folder="cares")
        return cmake

    def build(self):
        cmake = self.cmake_configure()
        cmake.build()
        cmake.install()

    def package(self):
        return

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.defines.append("CARES_STATICLIB")
        self.env_info.LD_LIBRARY_PATH.append("{}/lib".format(
            self.package_folder))
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
        self.cpp_info.includedirs = ['include']
        self.env_info.CPATH.append("{}/include".format(self.package_folder))
