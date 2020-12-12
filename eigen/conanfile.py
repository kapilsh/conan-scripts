from conans import ConanFile, CMake
from conans.tools import unzip
import os
import re
import shutil


class EigenConan(ConanFile):
    name = "eigen"
    with open(os.path.join(os.path.dirname(os.path.realpath(
            __file__)), "VERSION.txt"), 'r') as version_file:
        version = version_file.read()
    settings = {}
    description = "Eigen Matrix Algebra Library"
    generators = "cmake", "virtualenv"
    exports = "VERSION.txt"

    url = "http://eigen.tuxfamily.org/index.php?title=Main_Page"
    license = "http://eigen.tuxfamily.org/index.php?title=Main_Page#License"

    def source(self):
        tarball = "eigen-{}.tar.gz".format(self.version, self.version)
        os.system(
            "wget https://gitlab.com/libeigen/eigen/-/archive/{}/{}".format(
                self.version, tarball))
        unzip(tarball)
        eigen_reg = re.compile("eigen")
        eigen_dir = [x for x in os.listdir(os.curdir) if eigen_reg.search(x)][0]
        shutil.move(eigen_dir, "Eigen")
        os.unlink(tarball)

    def config(self):
        self.options.remove("os")
        self.options.remove("compiler")
        self.options.remove("shared")
        self.options.remove("build_type")
        self.options.remove("arch")

    def build(self):
        cmake = CMake(self)
        args = "-DCMAKE_INSTALL_PREFIX={}".format(self.package_folder)
        cmd = "mkdir -p Eigen/build && cd Eigen/build && " \
              "cmake .. {} && cmake --build . --target install {} --  -j12" \
              "".format(args, cmake.build_config)
        self.run(cmd)

    def package(self):
        cmd = f"mv {self.package_folder}/include/eigen3/Eigen " \
              f"{self.package_folder}/include/ && rm -r " \
              f"{self.package_folder}/include/eigen3"
        self.run(cmd)

    def package_info(self):
        self.cpp_info.includedirs = ['include']
        self.env_info.CPATH.append("{}/include".format(self.package_folder))
