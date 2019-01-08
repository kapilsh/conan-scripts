import os
import sys
import shutil

from conans import ConanFile, CMake
from conans.tools import download, unzip, replace_in_file

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class CppZmqConan(ConanFile):
    with open(os.path.join(os.path.dirname(os.path.realpath(
            __file__)), "VERSION.txt"), 'r') as version_file:
        version = version_file.read()

    zmq_version = "4.2.5"

    name = "cppzmq"
    requires = f"zmq/{zmq_version}@kapilsh/release"

    license = "https://github.com/zeromq/cppzmq/blob/master/LICENSE"
    url = "https://github.com/zeromq/cppzmq"
    description = "Header-only C++ binding for libzmq"
    settings = {}
    generators = "cmake", "virtualenv"
    exports = "VERSION.txt", "../gcc.py"

    download_url = "https://github.com/zeromq/cppzmq/archive"

    def source(self):
        tar_file = "v{}.tar.gz".format(self.version)
        download("{}/{}".format(self.download_url, tar_file), tar_file)
        unzip(tar_file)
        os.unlink(tar_file)
        shutil.move("cppzmq-{}".format(self.version), "cppzmq")
        replace_in_file(os.path.join("cppzmq", 'CMakeLists.txt'),
                        'CMAKE_SOURCE_DIR', 'CMAKE_CURRENT_SOURCE_DIR')
        replace_in_file(os.path.join("cppzmq", 'CMakeLists.txt'),
                        'find_package(ZeroMQ QUIET)',
                        'find_package(ZeroMQ PATHS {}/share/cmake/'
                        'ZeroMQ NO_DEFAULT_PATH REQUIRED)'.format(
                            self.deps_cpp_info["zmq"].rootpath))

    def build(self):
        cmake = CMake(self)
        cmake.definitions["ZeroMQ_ROOT_DIR"] = self.deps_cpp_info[
            "zmq"].rootpath
        cmake.configure(source_folder='cppzmq')
        cmake.build()
        cmake.install()

    def package(self):
        pass

    def package_info(self):
        self.cpp_info.includedirs = ['include']
        self.env_info.CPATH.append("{}/include".format(self.package_folder))
