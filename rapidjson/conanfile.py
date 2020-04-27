import os
import shutil

from conans import ConanFile
from conans.tools import download, unzip


class RapidjsonConan(ConanFile):
    with open(os.path.join(os.path.dirname(os.path.realpath(
            __file__)), "VERSION.txt"), 'r') as version_file:
        version = version_file.read()

    name = "rapidjson"
    description = "A fast JSON parser/generator for C++"
    settings = {}
    url = "https://github.com/Tencent/rapidjson/"
    license = "MIT"
    generators = "cmake", "virtualenv"
    exports = "VERSION.txt"

    github_url = "https://github.com/Tencent/rapidjson/archive/"

    def config(self):
        self.options.remove("os")
        self.options.remove("compiler")
        self.options.remove("shared")
        self.options.remove("build_type")
        self.options.remove("arch")

    def source(self):
        tar_file = "v{}.tar.gz".format(self.version)
        download("{}/{}".format(self.github_url, tar_file), tar_file)
        unzip(tar_file)
        os.unlink(tar_file)
        shutil.move("rapidjson-{}".format(self.version), "rapidjson")

    def package(self):
        include_folder = os.path.join("rapidjson", "include")
        self.copy(pattern="*", dst="include", src=include_folder)

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.includedirs = ['include']
        self.env_info.CPATH.append("{}/include".format(self.package_folder))
