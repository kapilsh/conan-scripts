import multiprocessing
import os
import sys
import shutil

from conans import ConanFile
from conans.tools import download, unzip, chdir

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class ZmqConan(ConanFile):
    from gcc import GCC_VERSIONS, CURRENT_GCC_VERSION

    with open(os.path.join(os.path.dirname(os.path.realpath(
            __file__)), "VERSION.txt"), 'r') as version_file:
        version = version_file.read()
    name = "tbb"

    requires = f"gcc/{CURRENT_GCC_VERSION}@kapilsh/release"
    license = "https://github.com/01org/tbb/blob/tbb_2019/LICENSE"
    url = "https://github.com/01org/tbb"
    description = "Threading Building Blocks (Intel TBB)"
    settings = {"os": ["Linux"],
                "compiler": {"gcc": {"version": GCC_VERSIONS}},
                "arch": ["x86_64"],
                "build_type": ["Debug", "Release"]}
    options = {"shared": [True, False]}
    default_options = "shared=False"
    generators = "cmake", "virtualenv"
    exports = "../gcc.py", "VERSION.txt"

    download_url = "https://github.com/01org/tbb/archive"

    def source(self):
        tar_file = "{}.tar.gz".format(self.version)
        download("{}/{}".format(self.download_url, tar_file), tar_file)
        unzip(tar_file)
        os.unlink(tar_file)
        shutil.move("tbb-{}".format(self.version), "tbb")

    def build(self):
        extra = "" if self.options.shared else "extra_inc=big_iron.inc"
        arch = "intel64"
        num_threads = int(multiprocessing.cpu_count() / 2)
        with chdir("tbb"):
            self.run(f"make -j{num_threads} arch={arch} {extra}")

    def package(self):
        self.copy("*.h", "include", "tbb/include")
        self.copy("*", "include/tbb/compat", "tbb/include/tbb/compat")
        build_folder = "tbb/build/"
        build_type = "debug" if self.settings.build_type == "Debug" \
            else "release"
        self.copy("*%s*.a" % build_type, dst="lib", src=build_folder,
                  keep_path=False)

    def package_info(self):
        if self.settings.build_type == "Debug":
            self.cpp_info.libs.extend(["tbb_debug", "tbbmalloc_debug"])
            if self.options.shared:
                self.cpp_info.libs.extend(["tbbmalloc_proxy_debug"])
        else:
            self.cpp_info.libs.extend(["tbb", "tbbmalloc"])
            if self.options.shared:
                self.cpp_info.libs.extend(["tbbmalloc_proxy"])
        self.env_info.LD_LIBRARY_PATH.append("{}/lib".format(
            self.package_folder))
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
        self.cpp_info.includedirs = ['include']
        self.env_info.CPATH.append("{}/include".format(self.package_folder))
