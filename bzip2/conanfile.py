import os
import sys
import shutil

from conans import ConanFile, CMake
from conans.client.tools import download, check_md5, unzip, \
    chdir, replace_in_file

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class Bzip2Conan(ConanFile):
    from gcc import GCC_VERSIONS, CURRENT_GCC_VERSION

    name = "bzip2"

    with open(os.path.join(os.path.dirname(os.path.realpath(
            __file__)), "VERSION.txt"), 'r') as version_file:
        version = version_file.read()

    settings = {"os": ["Linux"],
                "compiler": {"gcc": {"version": GCC_VERSIONS}},
                "arch": ["x86_64"],
                "build_type": ["Debug", "Release"]}

    requires = f"gcc/{CURRENT_GCC_VERSION}@kapilsh/release"

    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = "shared=False", "fPIC=True"

    generators = "cmake", "virtualenv"
    exports = "CMakeLists.txt", "VERSION.txt", "../gcc.py"
    url = "http://www.bzip.org/"
    license = "BSD-style license"

    description = "bzip2 is a freely available, patent free (see below), " \
                  "high-quality data compressor. It typically compresses " \
                  "files to within 10% to 15% of the best  available " \
                  "techniques (the PPM family of statistical compressors), " \
                  "whilst being around twice as fast at compression " \
                  "and six times faster at decompression."

    @property
    def zip_folder_name(self):
        return f"bzip2-{self.version}"

    def source(self):
        zip_name = f"bzip2-{self.version}.tar.gz"
        url = f"https://bintray.com/conan/Sources/download_file?" \
              f"file_path={zip_name}"
        download(url, zip_name)
        check_md5(zip_name, "00b516f4704d4a7cb50a1d97e6e8e15b")
        unzip(zip_name)
        os.unlink(zip_name)

    def build(self):
        shutil.move("CMakeLists.txt", f"{self.zip_folder_name}/CMakeLists.txt")
        with chdir(self.zip_folder_name):
            replace_in_file("bzip2.c", "sys\\stat.h", "sys/stat.h")
            os.mkdir("_build")
            with chdir("_build"):
                cmake = CMake(self)
                if self.options.fPIC:
                    cmake.definitions["FPIC"] = "ON"
                cmake.configure(build_dir=".", source_dir="..")
                cmake.build(build_dir=".")

    def package(self):
        self.copy("bzlib.h", dst="include", src=self.zip_folder_name,
                  keep_path=False)
        self.copy("*bzip2", dst="bin", src=self.zip_folder_name,
                  keep_path=False)
        self.copy(pattern="*.a", dst="lib",
                  src=f"{self.zip_folder_name}/_build", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ['bz2']
        self.env_info.LD_LIBRARY_PATH.append("{}/lib".format(
            self.package_folder))
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
        self.cpp_info.includedirs = ['include']
        self.env_info.CPATH.append("{}/include".format(self.package_folder))
