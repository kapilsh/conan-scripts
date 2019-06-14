from conans import ConanFile, CMake
from conans.tools import unzip, download
import os
import shutil


class WebsocketppConan(ConanFile):
    name = "yaml-cpp"

    with open(os.path.join(os.path.dirname(os.path.realpath(
            __file__)), "VERSION.txt"), 'r') as version_file:
        version = version_file.read()

    settings = "os", "arch", "compiler", "build_type"
    description = "A YAML parser and emitter in C++"
    generators = "cmake", "virtualenv"

    exports = "VERSION.txt"

    url = "https://github.com/jbeder/yaml-cpp"
    license = "https://github.com/jbeder/yaml-cpp/blob/master/LICENSE"

    github_url = "https://github.com/jbeder/yaml-cpp/archive"

    def source(self):
        tar_file = "{}-{}.tar.gz".format(self.name, self.version)
        download("{}/{}".format(self.github_url, tar_file), tar_file)
        unzip(tar_file)
        os.unlink(tar_file)
        shutil.move(f"{self.name}-{self.name}-{self.version}", self.name)

    def build(self):
        cmake = CMake(self)
        cmake.configure(source_folder=self.name)
        cmake.build()
        cmake.install()

    def package(self):
        pass

    def package_info(self):
        self.cpp_info.includedirs = ['include']
        self.env_info.CPATH.append("{}/include".format(self.package_folder))
