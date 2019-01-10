import os
import sys
import shutil

from conans import ConanFile, CMake
from conans.tools import download, unzip, collect_libs

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class GladConan(ConanFile):
    from gcc import GCC_VERSIONS, CURRENT_GCC_VERSION

    with open(os.path.join(os.path.dirname(os.path.realpath(
            __file__)), "VERSION.txt"), 'r') as version_file:
        version = version_file.read()

    name = "glad"

    requires = f"gcc/{CURRENT_GCC_VERSION}@kapilsh/release"
    license = "MIT"
    url = "https://github.com/Dav1dde/glad"
    description = "Multi-Language Vulkan/GL/GLES/EGL/GLX/WGL " \
                  "Loader-Generator based on the official specs"
    settings = {"os": ["Linux"],
                "compiler": {"gcc": {"version": GCC_VERSIONS}},
                "arch": ["x86_64"],
                "build_type": ["Debug", "Release"]}
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "profile": ["compatibility", "core"],
        "api_type": "ANY",
        "api_version": "ANY",
        "extensions": "ANY",
        "spec": ["gl", "egl", "glx", "wgl"],
        "no_loader": [True, False]
    }
    default_options = (
        "shared=False",
        "fPIC=True",
        "profile=compatibility",
        "api_type=gl",
        "api_version=3.0",
        "extensions=''",
        "spec=gl",
        "no_loader=False"
    )
    generators = "cmake"
    exports = "VERSION.txt", "../gcc.py"

    github_link = "https://github.com/Dav1dde/glad/archive"

    def source(self):
        tar_file = f"v{self.version}.tar.gz"
        download(f"{self.github_link}/{tar_file}", tar_file)
        unzip(tar_file)
        os.unlink(tar_file)
        shutil.move("glad-{}".format(self.version), "glad")

    def build(self):
        cmake = CMake(self)
        cmake.definitions["GLAD_PROFILE"] = self.options.profile
        cmake.definitions["GLAD_API"] = "%s=%s" % (
            self.options.api_type, self.options.api_version)
        cmake.definitions["GLAD_EXTENSIONS"] = self.options.extensions
        cmake.definitions["GLAD_SPEC"] = self.options.spec
        cmake.definitions["GLAD_NO_LOADER"] = self.options.no_loader
        cmake.definitions[
            "GLAD_GENERATOR"] = "c" if \
            self.settings.build_type == "Release" else "c-debug"
        cmake.definitions["GLAD_EXPORT"] = True
        cmake.definitions["GLAD_INSTALL"] = True
        cmake.configure(source_dir="glad")
        cmake.build()
        cmake.install()

    def package(self):
        pass

    def package_info(self):
        self.cpp_info.libs = collect_libs(self)
        self.cpp_info.libs.append("dl")
        lib_path = "{}/lib".format(self.package_folder)
        self.cpp_info.libdirs = [lib_path]
        self.env_info.LD_LIBRARY_PATH.append(lib_path)
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
        self.cpp_info.includedirs = ['include']
        self.env_info.CPATH.append("{}/include".format(self.package_folder))
