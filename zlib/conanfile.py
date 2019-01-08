import shutil
import sys

from conans import ConanFile, CMake, tools
import os

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class GflagsConan(ConanFile):
    from gcc import GCC_VERSIONS, CURRENT_GCC_VERSION

    with open(os.path.join(os.path.dirname(os.path.realpath(
            __file__)), "VERSION.txt"), 'r') as version_file:
        version = version_file.read()

    description = "A massively spiffy yet delicately unobtrusive " \
                  "compression library"
    url = "https://zlib.net/"
    name = "zlib"
    license = "https://github.com/madler/zlib/blob/master/zlib.h"
    requires = f"gcc/{CURRENT_GCC_VERSION}@kapilsh/release"
    exports = "VERSION.txt", "../gcc.py"
    generators = "cmake"
    settings = {"os": ["Linux"],
                "compiler": {"gcc": {"version": GCC_VERSIONS}},
                "arch": ["x86_64"],
                "build_type": ["Debug", "Release"]}
    options = {"shared": [True, False],
               "fPIC": [True, False],
               "nothreads": [True, False]}
    default_options = "shared=False", "fPIC=True", "nothreads=True"
    source_url = "https://github.com/madler/zlib/archive"

    def source(self):
        tar_file = f"v{self.version}.tar.gz"
        tools.download("{}/{}".format(self.source_url, tar_file), tar_file)
        tools.unzip(tar_file)
        os.unlink(tar_file)
        shutil.move(f"zlib-{self.version}", "zlib")

    def build(self):
        cmake = CMake(self)
        cmake.definitions["CMAKE_BUILD_TYPE"] = self.settings.build_type
        cmake.definitions["BUILD_SHARED_LIBS"] = self.options.shared
        cmake.definitions["BUILD_STATIC_LIBS"] = not self.options.shared
        cmake.definitions["CMAKE_INSTALL_PREFIX"] = "install"
        cmake.configure(source_folder="zlib")
        cmake.build()
        cmake.install()

    def package(self):
        self.copy("*", dst="include", src="install/include")
        self.copy("*.a", dst="lib", src="install/lib")
        self.copy("*", dst="bin", src="install/bin")

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.env_info.LD_LIBRARY_PATH.append("{}/lib".format(
            self.package_folder))
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
        self.cpp_info.includedirs = ['include']
        self.env_info.CPATH.append("{}/include".format(self.package_folder))
