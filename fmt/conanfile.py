import sys
import os
import shutil

from conans import ConanFile, CMake, tools
from conans.tools import download, unzip

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class FmtConan(ConanFile):
    from gcc import GCC_VERSIONS, CURRENT_GCC_VERSION

    with open(os.path.join(os.path.dirname(os.path.realpath(
            __file__)), "VERSION.txt"), 'r') as version_file:
        version = version_file.read()

    name = "fmt"
    requires = f"gcc/{CURRENT_GCC_VERSION}@kapilsh/release"
    license = "https://github.com/fmtlib/fmt/blob/master/LICENSE.rst"
    url = "https://github.com/fmtlib/fmt"
    description = "A modern formatting library "
    settings = {"os": ["Linux"],
                "compiler": {"gcc": {"version": GCC_VERSIONS}},
                "arch": ["x86_64"],
                "build_type": ["Debug", "Release"]}
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = "shared=False", "fPIC=True"
    generators = "cmake", "virtualenv"
    exports = "../gcc.py", "VERSION.txt"

    download_url = "https://github.com/fmtlib/fmt/archive"

    def source(self):
        tar_file = "{}.tar.gz".format(self.version)
        download("{}/{}".format(self.download_url, tar_file), tar_file)
        unzip(tar_file)
        os.unlink(tar_file)
        shutil.move("fmt-{}".format(self.version), "fmt")

    def build(self):
        cmake = CMake(self)
        cmake.definitions["FMT_DOC"] = False
        cmake.definitions["FMT_TEST"] = False
        cmake.definitions["FMT_INSTALL"] = True
        cmake.configure(source_dir="fmt")
        cmake.build()
        cmake.install()

    def package(self):
        return

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.libs.append("fmt")
        self.env_info.LD_LIBRARY_PATH.append("{}/lib64".format(
            self.package_folder))
        self.cpp_info.includedirs = ['include']
        self.env_info.CPATH.append("{}/include".format(self.package_folder))
