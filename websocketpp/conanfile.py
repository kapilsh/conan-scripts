from conans import ConanFile, CMake
from conans.tools import unzip, download
import os
import shutil


class WebsocketppConan(ConanFile):
    name = "websocketpp"
    boost_version = "1.68.0"
    openssl_version = "1.1.1"
    zlib_version = "1.2.11"

    with open(os.path.join(os.path.dirname(os.path.realpath(
            __file__)), "VERSION.txt"), 'r') as version_file:
        version = version_file.read()
    settings = "os", "arch", "compiler", "build_type"
    description = "C++ websocket client/server library"
    generators = "cmake", "virtualenv"

    requires = f"boost/{boost_version}@kapilsh/release", \
               f"openssl/{openssl_version}@kapilsh/release"

    exports = "VERSION.txt"

    url = "https://github.com/zaphoyd/websocketpp"
    license = "http://eigen.tuxfamily.org/index.php?title=Main_Page#License"

    github_url = "https://github.com/zaphoyd/websocketpp/archive"

    def source(self):
        tar_file = "{}.tar.gz".format(self.version)
        download("{}/{}".format(self.github_url, tar_file), tar_file)
        unzip(tar_file)
        os.unlink(tar_file)
        shutil.move(f"websocketpp-{self.version}", "websocketpp")

    def build(self):
        cmake = CMake(self)
        cmake.definitions['BUILD_TESTS'] = False
        cmake.definitions['BUILD_EXAMPLES'] = False
        cmake.configure(source_folder="websocketpp")
        cmake.build()
        cmake.install()

    def package(self):
        pass

    def package_info(self):
        self.cpp_info.includedirs = ['include']
        self.env_info.CPATH.append("{}/include".format(self.package_folder))
