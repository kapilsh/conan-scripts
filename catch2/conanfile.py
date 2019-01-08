import os

from conans import ConanFile
from conans.tools import download


class Catch2Conan(ConanFile):
    with open(os.path.join(os.path.dirname(os.path.realpath(
            __file__)), "VERSION.txt"), 'r') as version_file:
        version = version_file.read()

    name = "catch2"
    license = "https://github.com/catchorg/Catch2/blob/master/LICENSE.txt"
    url = "https://github.com/catchorg/Catch2"
    description = "A modern, C++-native, header-only, test framework for " \
                  "unit-tests"
    settings = {}
    generators = "cmake", "virtualenv"
    exports = "VERSION.txt"

    download_url = "https://github.com/catchorg/Catch2/releases/download"

    def config(self):
        self.options.remove("os")
        self.options.remove("compiler")
        self.options.remove("shared")
        self.options.remove("build_type")
        self.options.remove("arch")

    def source(self):
        source_file = f"v{self.version}/catch.hpp"
        download("{}/{}".format(self.download_url, source_file), "catch.hpp")

    def package(self):
        self.copy("catch.hpp", "include", ".")

    def package_info(self):
        self.cpp_info.includedirs = ['include']
        self.env_info.CPATH.append("{}/include".format(self.package_folder))
