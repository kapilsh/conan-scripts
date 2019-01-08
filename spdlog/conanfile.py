import sys
import os
import shutil

from conans import ConanFile, CMake
from conans.tools import download, unzip

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class SpdLogConan(ConanFile):
    with open(os.path.join(os.path.dirname(os.path.realpath(
            __file__)), "VERSION.txt"), 'r') as version_file:
        version = version_file.read()

    name = "spdlog"
    settings = {}
    description = "Fast C++ logging library"
    generators = "cmake", "virtualenv"

    exports = "VERSION.txt"

    license = "https://github.com/gabime/spdlog/blob/v1.x/LICENSE"
    url = "https://github.com/gabime/spdlog"

    download_url = "https://github.com/gabime/spdlog/archive"

    def config(self):
        self.options.remove("os")
        self.options.remove("compiler")
        self.options.remove("shared")
        self.options.remove("build_type")
        self.options.remove("arch")

    def source(self):
        tar_file = "v{}.tar.gz".format(self.version)
        download("{}/{}".format(self.download_url, tar_file), tar_file)
        unzip(tar_file)
        os.unlink(tar_file)
        shutil.move("spdlog-{}".format(self.version), "spdlog")

    def build(self):
        cmake = CMake(self)
        cmake.definitions["SPDLOG_BUILD_EXAMPLES"] = False
        cmake.definitions["SPDLOG_BUILD_TESTING"] = False
        cmake.definitions["SPDLOG_BUILD_BENCH"] = False
        cmake.configure(source_dir="spdlog")
        cmake.build()
        cmake.install()

    def package(self):
        return

    def package_info(self):
        self.cpp_info.includedirs = ['include']
        self.env_info.CPATH.append("{}/include".format(self.package_folder))
