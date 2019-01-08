import os
import shutil
import sys

from conans import ConanFile, tools, AutoToolsBuildEnvironment
from conans.tools import download, unzip, environment_append


sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class ProtocolBuffersConan(ConanFile):
    from gcc import GCC_VERSIONS, CURRENT_GCC_VERSION

    with open(os.path.join(os.path.dirname(os.path.realpath(
            __file__)), "VERSION.txt"), 'r') as version_file:
        version = version_file.read()

    requires = f"gcc/{CURRENT_GCC_VERSION}@kapilsh/release"
    name = "protobuf"
    license = "https://github.com/protocolbuffers/protobuf/blob/master/LICENSE"
    url = "https://github.com/protocolbuffers/protobuf"
    description = "Protocol Buffers Serialization Library"
    exports = "VERSION.txt", "../gcc.py"
    generators = "cmake"
    settings = {"os": ["Linux"],
                "compiler": {"gcc": {"version": GCC_VERSIONS}},
                "arch": ["x86_64"],
                "build_type": ["Debug", "Release"]}
    options = {"shared": [True, False]}
    default_options = "shared=False"

    github_link = "https://github.com/protocolbuffers/protobuf/releases/" \
                  "download"

    def source(self):
        tar_file = "v{}/protobuf-cpp-{}.tar.gz".format(
            self.version, self.version)
        download("{}/{}".format(self.github_link, tar_file), tar_file)
        unzip(tar_file)
        os.unlink(tar_file)
        shutil.move("protobuf-{}".format(self.version), "protobuf")

    def build(self):
        env_build = AutoToolsBuildEnvironment(self)
        with environment_append(env_build.vars):
            self.run(f"cd protobuf && chmod +x configure && "
                     f"./configure --prefix=/tmp/protobuf/ --disable-shared &&"
                     f" make -j6 && make install")

    def package(self):
        self.copy("*", dst="include", src="/tmp/protobuf/include")
        self.copy("*.a", dst="lib", src="/tmp/protobuf/lib")
        self.copy("*", dst="bin", src="/tmp/protobuf/bin")

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.env_info.LD_LIBRARY_PATH.append("{}/lib".format(
            self.package_folder))
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
        self.cpp_info.includedirs = ['include']
        self.env_info.CPATH.append("{}/include".format(self.package_folder))
