import os
import sys
import shutil

from conans import ConanFile, CMake
from conans.tools import download, unzip, os_info, SystemPackageTool

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class GlfwConan(ConanFile):
    from gcc import GCC_VERSIONS, CURRENT_GCC_VERSION

    with open(os.path.join(os.path.dirname(os.path.realpath(
            __file__)), "VERSION.txt"), 'r') as version_file:
        version = version_file.read()

    name = "glfw"

    requires = f"gcc/{CURRENT_GCC_VERSION}@kapilsh/release"
    license = "https://github.com/glfw/glfw/blob/master/LICENSE.md"
    url = "https://www.glfw.org/"
    description = "A multi-platform library for OpenGL, OpenGL ES, Vulkan, " \
                  "window and input"
    settings = {"os": ["Linux"],
                "compiler": {"gcc": {"version": GCC_VERSIONS}},
                "arch": ["x86_64"],
                "build_type": ["Debug", "Release"]}
    options = {"shared": [True, False]}
    default_options = "shared=False"
    generators = "cmake"
    exports = "VERSION.txt", "../gcc.py"

    github_link = "https://github.com/glfw/glfw/archive"

    def system_requirements(self):
        if os_info.is_linux:
            if os_info.with_apt:
                installer = SystemPackageTool()
                arch_suffix = ':i386'
                installer.install("g++-multilib")
                installer.install("xorg-dev")
                installer.install(f"libx11-dev{arch_suffix}")
                installer.install(f"libxrandr-dev{arch_suffix}")
                installer.install(f"libxinerama-dev{arch_suffix}")
                installer.install(f"libxcursor-dev{arch_suffix}")
                installer.install(f"libxi-dev{arch_suffix}")
                installer.install("libgl1-mesa-dev")
            elif os_info.with_yum:
                installer = SystemPackageTool()
                arch_suffix = '.i686'
                installer.install("glibmm24.i686")
                installer.install("glibc-devel.i686")
                installer.install("libXrender-devel.i686")
                installer.install("libdrm-devel.i686")
                installer.install("libXdamage-devel.i686")
                installer.install("libxcb-devel.i686")
                installer.install("libX11-devel.i686")
                installer.install("libXxf86vm-devel.i686")
                installer.install("libXfixes-devel.i686")
                installer.install("libXext-devel.i686")
                installer.install("mesa-libGL-devel.i686")
                installer.install("libXau-devel.i686")
                installer.install(f"mesa-libGLU-devel{arch_suffix}")
                installer.install(f"xorg-x11-server-devel{arch_suffix}")
                installer.install(f"libXrandr-devel{arch_suffix}")
                installer.install(f"libXinerama-devel{arch_suffix}")
                installer.install(f"libXcursor-devel{arch_suffix}")
                installer.install(f"libXi-devel{arch_suffix}")
            else:
                self.output.warn(
                    "Could not determine package manager, skipping Linux "
                    "system requirements installation.")

    def source(self):
        tar_file = "{}.tar.gz".format(self.version)
        download(f"{self.github_link}/{tar_file}", tar_file)
        unzip(tar_file)
        os.unlink(tar_file)
        shutil.move("glfw-{}".format(self.version), "glfw")

    def build(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_SHARED_LIBS"] = self.options.shared
        cmake.definitions["GLFW_BUILD_EXAMPLES"] = False
        cmake.definitions["GLFW_BUILD_TESTS"] = False
        cmake.definitions["GLFW_BUILD_DOCS"] = False
        cmake.configure(source_dir="glfw")
        cmake.build()

    def package(self):
        self.copy(pattern="*.h", dst="include", src="glfw/include",
                  keep_path=True)
        if self.options.shared:
            self.copy(pattern="*.so*", dst="lib", keep_path=False)
        else:
            self.copy(pattern="*.a", dst="lib", keep_path=False)

    def package_info(self):
        if self.options.shared:
            self.cpp_info.libs = ['glfw']
            self.cpp_info.exelinkflags.append("-lrt -lm -ldl")
        else:
            self.cpp_info.libs = ['glfw3']
            self.cpp_info.libs.extend(
                ['Xrandr', 'Xrender', 'Xi', 'Xinerama', 'Xcursor', 'GL',
                 'm', 'dl', 'drm', 'Xdamage', 'X11-xcb', 'xcb-glx',
                 'xcb-dri2', 'xcb-dri3', 'xcb-present', 'xcb-sync',
                 'Xxf86vm', 'Xfixes', 'Xext', 'X11', 'pthread', 'xcb',
                 'Xau'])

        lib_path = "{}/lib".format(self.package_folder)
        self.cpp_info.libdirs = [lib_path]
        self.env_info.LD_LIBRARY_PATH.append(lib_path)
        self.cpp_info.includedirs = ['include']
        self.env_info.CPATH.append("{}/include".format(self.package_folder))
