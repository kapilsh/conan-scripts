import os
import sys
import shutil

from conans import ConanFile, CMake
from conans.client.tools import download, collect_libs, unzip

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class ImguiConan(ConanFile):
    from gcc import GCC_VERSIONS, CURRENT_GCC_VERSION

    name = "imgui"

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
    exports_sources = "imgui_demo.h", "imgui_demo.cpp"
    url = "https://github.com/ocornut/imgui"
    license = "MIT"

    description = "Bloat-free Immediate Mode Graphical User interface for " \
                  "C++ with minimal dependencies"

    @property
    def zip_folder_name(self):
        return f"bzip2-{self.version}"

    def source(self):
        tar_file = f"v{self.version}.tar.gz"
        download(f"{self.url}/archive/{tar_file}", tar_file)
        unzip(tar_file)
        os.unlink(tar_file)
        shutil.move("imgui-{}".format(self.version), "imgui")

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
        cmake.install()

    def package(self):
        pass

    def package_info(self):
        self.cpp_info.libs = collect_libs(self)
        self.env_info.LD_LIBRARY_PATH.append("{}/lib".format(
            self.package_folder))
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
        self.cpp_info.includedirs = ['include']
        self.env_info.CPATH.append("{}/include".format(self.package_folder))
