"openssl-1.1.1.tar.gz"

import os
import shutil
import sys

from conans import ConanFile, tools, AutoToolsBuildEnvironment
from conans.tools import download, unzip, environment_append

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class OpenSSLConan(ConanFile):
    from gcc import GCC_VERSIONS, CURRENT_GCC_VERSION

    with open(os.path.join(os.path.dirname(os.path.realpath(
            __file__)), "VERSION.txt"), 'r') as version_file:
        version = version_file.read()

    requires = f"gcc/{CURRENT_GCC_VERSION}@kapilsh/release", \
               "zlib/1.2.11@kapilsh/release"
    name = "openssl"
    license = "https://github.com/openssl/openssl/blob/master/LICENSE"
    url = "https://www.openssl.org"
    description = "SSL and Crypto"
    exports = "VERSION.txt", "../gcc.py"
    generators = "cmake"
    settings = {"os": ["Linux"],
                "compiler": {"gcc": {"version": GCC_VERSIONS}},
                "arch": ["x86_64"],
                "build_type": ["Debug", "Release"]}
    options = {"shared": [True, False]}
    default_options = "shared=False"

    source_url = "https://www.openssl.org/source/"

    def source(self):
        tar_file = f"openssl-{self.version}.tar.gz"
        download("{}/{}".format(self.source_url, tar_file), tar_file)
        unzip(tar_file)
        os.unlink(tar_file)
        shutil.move("openssl-{}".format(self.version), "openssl")

    def build(self):
        env_build = AutoToolsBuildEnvironment(self)
        with environment_append(env_build.vars):
            self.run(f"cd openssl && chmod +x config && ./config "
                     f"--prefix=/tmp/openssl && make -j6 && "
                     f"make install")

    def package(self):
        self.copy("*", dst="include", src="/tmp/openssl/include")
        self.copy("*.a", dst="lib", src="/tmp/openssl//lib")
        self.copy("*", dst="bin", src="/tmp/openssl/bin")

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.env_info.LD_LIBRARY_PATH.append("{}/lib".format(
            self.package_folder))
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
        self.cpp_info.includedirs = ['include']
        self.env_info.CPATH.append("{}/include".format(self.package_folder))
