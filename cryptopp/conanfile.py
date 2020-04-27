import os
import sys

from conans import ConanFile, CMake, tools
from conans.tools import download, unzip

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class CryptoPPConan(ConanFile):
    from gcc import GCC_VERSIONS, CURRENT_GCC_VERSION

    with open(os.path.join(os.path.dirname(os.path.realpath(
            __file__)), "VERSION.txt"), 'r') as version_file:
        version = version_file.read()
    name = "cryptopp"
    url = "https://www.cryptopp.com"
    license = "BSL-1.0"
    description = "Free C++ class library of cryptographic schemes"
    requires = f"gcc/{CURRENT_GCC_VERSION}@kapilsh/release"
    settings = {"os": ["Linux"],
                "compiler": {"gcc": {"version": GCC_VERSIONS}},
                "arch": ["x86_64"],
                "build_type": ["Debug", "Release"]}
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {'shared': False, 'fPIC': True}
    generators = "cmake"
    exports = "VERSION.txt", "../gcc.py"

    def source(self):
        zip_file = "cryptopp{}.zip".format(self.version.replace('.', ''))
        download("http://www.cryptopp.com/{}".format(zip_file), zip_file,
                 verify=False)
        unzip(zip_file)
        os.unlink(zip_file)
        os.system("ls -al")

    def build(self):
        if self.options.shared:
            self.run("make -j6 dynamic")
        else:
            self.run("make -j6 static")

    def package(self):
        self.copy(pattern="*.h", dst="include/cryptopp", src=".")
        self.copy(pattern="*.so", dst="lib", src=".", keep_path=False)
        self.copy(pattern="*.a", dst="lib", src=".", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["cryptopp"]
