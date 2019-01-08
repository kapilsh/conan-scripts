import os
import re
import sys
import shutil

from conans import ConanFile, CMake
from conans.client.tools import collect_libs
from conans.tools import download, unzip, replace_in_file

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class ZmqConan(ConanFile):
    from gcc import GCC_VERSIONS, CURRENT_GCC_VERSION

    with open(os.path.join(os.path.dirname(os.path.realpath(
            __file__)), "VERSION.txt"), 'r') as version_file:
        version = version_file.read()

    name = "zmq"

    requires = f"gcc/{CURRENT_GCC_VERSION}@kapilsh/release"

    license = "https://github.com/zeromq/libzmq/blob/master/COPYING"

    url = "https://github.com/zeromq/libzmq"

    description = "ZeroMQ core engine in C++, implements ZMTP/3.1"
    settings = {"os": ["Linux"],
                "compiler": {"gcc": {"version": GCC_VERSIONS}},
                "arch": ["x86_64"],
                "build_type": ["Debug", "Release"]}
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = "shared=False", "fPIC=True"
    generators = "cmake", "virtualenv"
    exports = "../gcc.py", "VERSION.txt"

    download_url = "https://github.com/zeromq/libzmq/archive"

    def source(self):
        tar_file = "v{}.tar.gz".format(self.version)
        download("{}/{}".format(self.download_url, tar_file), tar_file)
        unzip(tar_file)
        os.unlink(tar_file)
        shutil.move("libzmq-{}".format(self.version), "libzmq")
        replace_in_file(
            os.path.join("libzmq", 'CMakeLists.txt'),
            "if (MSVC)\n    "
            "# default for all sources is to use precompiled header",
            "if (MSVC_DISABLED)\n    "
            "# default for all sources is to use precompiled header")

        # fix PDB location
        replace_in_file(
            os.path.join("libzmq", 'CMakeLists.txt'),
            'install (FILES ${CMAKE_CURRENT_BINARY_DIR}/bin/libzmq',
            'install (FILES ${CMAKE_BINARY_DIR}/bin/libzmq')

    def build(self):
        cmake = CMake(self)
        cmake.definitions['ENABLE_CURVE'] = False
        cmake.definitions['WITH_LIBSODIUM'] = False
        cmake.definitions['CMAKE_INSTALL_LIBDIR'] = 'lib'
        cmake.definitions['ZMQ_BUILD_TESTS'] = False
        cmake.definitions['WITH_PERF_TOOL'] = False
        cmake.configure(source_folder='libzmq')
        cmake.build()

    def package(self):
        self.copy("*", dst="include", src="libzmq/include")
        self.copy("*.a", dst="lib", src="lib")
        self.copy("libzmq.pc", dst="lib/pkgconfig", src=".")
        self.copy("ZeroMQ*.cmake", dst="share/cmake/ZeroMQ/", src=".")

    def package_info(self):
        self.cpp_info.libs = collect_libs(self)
        self.env_info.LD_LIBRARY_PATH.append("{}/lib".format(
            self.package_folder))
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
        self.cpp_info.includedirs = ['include']
        self.env_info.CPATH.append("{}/include".format(self.package_folder))
        self.cpp_info.defines.append('ZMQ_STATIC')
        self.cpp_info.builddirs.append(
            os.path.join(self.package_folder, 'share', 'cmake', 'ZeroMQ'))
