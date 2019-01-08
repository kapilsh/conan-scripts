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

    description = "The gflags package contains a C++ library that " \
                  "implements commandline flags processing. "
    url = "https://github.com/gflags/gflags"
    name = "gflags"
    requires = f"gcc/{CURRENT_GCC_VERSION}@kapilsh/release"

    license = 'BSD 3-clause'
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
    source_url = "https://github.com/gflags/gflags/archive"

    def source(self):
        tar_file = f"v{self.version}.tar.gz"
        tools.download("{}/{}".format(self.source_url, tar_file), tar_file)
        tools.unzip(tar_file)
        os.unlink(tar_file)
        shutil.move(f"gflags-{self.version}", "gflags")

    def build(self):
        cmake = CMake(self)
        cmake.definitions["CMAKE_BUILD_TYPE"] = self.settings.build_type
        cmake.definitions["BUILD_SHARED_LIBS"] = self.options.shared
        cmake.definitions["BUILD_STATIC_LIBS"] = not self.options.shared
        cmake.definitions["BUILD_gflags_LIB"] = not self.options.nothreads
        cmake.definitions["BUILD_gflags_nothreads_LIB"] = \
            self.options.nothreads
        cmake.definitions["BUILD_PACKAGING"] = False
        cmake.definitions["BUILD_TESTING"] = False
        cmake.definitions["INSTALL_HEADERS"] = True
        cmake.definitions["INSTALL_SHARED_LIBS"] = self.options.shared
        cmake.definitions["INSTALL_STATIC_LIBS"] = not self.options.shared
        cmake.definitions["REGISTER_BUILD_DIR"] = False
        cmake.definitions["REGISTER_INSTALL_PREFIX"] = False
        cmake.configure(source_folder="gflags")
        cmake.build()
        cmake.install()

    def package(self):
        return

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.libs.extend(["pthread"])
        self.env_info.LD_LIBRARY_PATH.append("{}/lib".format(
            self.package_folder))
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
        self.cpp_info.includedirs = ['include']
        self.env_info.CPATH.append("{}/include".format(self.package_folder))
