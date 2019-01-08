import os
import sys
import shutil

from conans import ConanFile, CMake, tools
from conans.tools import download, unzip

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class FlatBuffersConan(ConanFile):
    from gcc import GCC_VERSIONS, CURRENT_GCC_VERSION

    with open(os.path.join(os.path.dirname(os.path.realpath(
            __file__)), "VERSION.txt"), 'r') as version_file:
        version = version_file.read()

    name = "flatbuffers"

    requires = f"gcc/{CURRENT_GCC_VERSION}@kapilsh/release"
    license = "https://github.com/google/flatbuffers/blob/master/LICENSE.txt"
    url = "https://github.com/google/flatbuffers"
    description = "Memory Efficient Serialization Library"
    settings = {"os": ["Linux"],
                "compiler": {"gcc": {"version": GCC_VERSIONS}},
                "arch": ["x86_64"],
                "build_type": ["Debug", "Release"]}
    options = {"shared": [True, False]}
    default_options = "shared=False"
    generators = "cmake"
    exports = "VERSION.txt", "../gcc.py"

    github_link = "https://github.com/google/flatbuffers/archive/"

    def source(self):
        tar_file = "v{}.tar.gz".format(self.version)
        download("{}/{}".format(self.github_link, tar_file), tar_file)
        unzip(tar_file)
        os.unlink(tar_file)
        shutil.move("flatbuffers-{}".format(self.version), "flatbuffers")

    def build(self):
        cmake = CMake(self)
        cmake.definitions["CMAKE_CXX_FLAGS"] = "-Wno-ignored-qualifiers"
        cmake.definitions["FLATBUFFERS_BUILD_TESTS"] = False
        cmake.definitions["FLATBUFFERS_BUILD_SHAREDLIB"] = self.options.shared
        cmake.configure(source_dir="flatbuffers")
        cmake.build()
        cmake.install()

    def package(self):
        self.copy(pattern="LICENSE.txt", dst="licenses")
        self.copy(pattern="flathash*", dst="bin", src="bin")

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.libs.append("flatbuffers")
        lib_path = "{}/lib64".format(self.package_folder)
        self.cpp_info.libdirs = [lib_path]
        self.env_info.LD_LIBRARY_PATH.append(lib_path)
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
        self.cpp_info.includedirs = ['include']
        self.env_info.CPATH.append("{}/include".format(self.package_folder))
