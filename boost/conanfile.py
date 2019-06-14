import os
import sys

from conans import ConanFile
from conans.tools import cpu_count, get, patch, chdir, environment_append, \
    save, which, collect_libs

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class BoostConan(ConanFile):
    from gcc import GCC_VERSIONS, CURRENT_GCC_VERSION

    bzip_version = "1.0.6"
    zlib_version = "1.2.11"

    signatures = {
        "1.66.0":
            "bd0df411efd9a585e5a2212275f8762079fed8842264954675a4fddc46cfcf60",
        "1.68.0":
            "da3411ea45622579d419bfda66f45cd0f8c32a181d84adfa936f5688388995cf"
    }

    name = "boost"

    lib_list = ['math', 'wave', 'container', 'contract', 'exception', 'graph',
                'iostreams', 'locale', 'log', 'program_options', 'random',
                'regex', 'mpi', 'serialization', 'signals', 'coroutine',
                'fiber', 'context', 'timer', 'thread', 'chrono', 'date_time',
                'atomic', 'filesystem', 'system', 'graph_parallel', 'python',
                'stacktrace', 'test', 'type_erasure']

    with open(os.path.join(os.path.dirname(os.path.realpath(
            __file__)), "VERSION.txt"), 'r') as version_file:
        version = version_file.read()

    settings = {"os": ["Linux"],
                "compiler": {"gcc": {"version": GCC_VERSIONS}},
                "arch": ["x86_64"],
                "build_type": ["Debug", "Release"]}

    requires = f"gcc/{CURRENT_GCC_VERSION}@kapilsh/release", \
               f"bzip2/{bzip_version}@kapilsh/release", \
               f"zlib/{zlib_version}@kapilsh/release"

    folder_name = "boost_{}".format(version.replace(".", "_"))
    description = "Boost provides free peer-reviewed portable " \
                  "C++ source libraries"

    options = {
        "shared": [True, False],
        "header_only": [True, False],
        "fPIC": [True, False],
        "skip_lib_rename": [True, False],
        "magic_autolink": [True, False]  # enables BOOST_ALL_NO_LIB
    }

    options.update(
        {"without_%s" % libname: [True, False] for libname in lib_list})

    default_options = ["shared=False", "header_only=False", "fPIC=True",
                       "skip_lib_rename=True", "magic_autolink=False"]

    default_options.extend(
        [f"without_{libname}=False" for libname in lib_list if
         libname != "python"])

    default_options.append("without_python=True")
    default_options.append("bzip2:shared=False")
    default_options.append("zlib:shared=False")
    default_options = tuple(default_options)

    url = "https://github.com/boostorg/boost"
    license = "Boost Software License - Version 1.0." \
              " http://www.boost.org/LICENSE_1_0.txt"
    short_paths = True
    no_copy_source = False

    exports = 'patches/*', "VERSION.txt", "../gcc.py"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.package_folder = None

    def source(self):
        sha256 = self.signatures[self.version]

        extension = ".tar.gz"

        zip_name = f"{self.folder_name}{extension}"
        url = f"https://dl.bintray.com/boostorg/release/" \
              f"{self.version}/source/{zip_name}"
        get(url, sha256=sha256)

    def build(self):

        if not self.options.without_python:
            patch(
                base_path=os.path.join(self.build_folder, self.folder_name),
                patch_file='patches/python_base_prefix.patch', strip=1)

        b2_exe = self.bootstrap()
        flags = self.get_build_flags()

        self.create_user_config_jam(self.build_folder)

        b2_flags = " ".join(flags)
        full_command = f"{b2_exe} {b2_flags} -j{cpu_count()} " \
                       f"--abbreviate-paths -d2"

        sources = os.path.join(self.source_folder, self.folder_name)

        full_command += f' --debug-configuration ' \
                        f'--build-dir="{self.build_folder}"'

        self.output.warn(full_command)

        with chdir(sources):
            with environment_append({"BOOST_BUILD_PATH": self.build_folder}):
                self.run(full_command)

    def get_build_flags(self):

        flags = ['address-model=64']

        if self.settings.compiler == "gcc":
            flags.append("--layout=system")

        flags.append("link={}".format(
            "static" if not self.options.shared else "shared"))
        if self.settings.build_type == "Debug":
            flags.append("variant=debug")
        else:
            flags.append("variant=release")

        for libname in self.lib_list:
            if getattr(self.options, "without_%s" % libname):
                flags.append("--without-%s" % libname)

        cxx_flags = []
        if self.options.fPIC:
            cxx_flags.append("-fPIC")
            flags.append("define=_GLIBCXX_USE_CXX11_ABI=1")

        cxx_flags = 'cxxflags="{}"'.format(
            " ".join(cxx_flags) if cxx_flags else "")
        flags.append(cxx_flags)
        flags.append("threading=multi")

        return flags

    def create_user_config_jam(self, folder):

        self.output.warn("Patching user-config.jam")

        contents = "\nusing zlib : {} : <include>{} <search>{} <name>{} ;" \
                   "".format(self.zlib_version,
                             self.deps_cpp_info["zlib"].include_paths[
                                 0].replace('\\', '/'),
                             self.deps_cpp_info["zlib"].lib_paths[0].replace(
                                 '\\', '/'),
                             self.deps_cpp_info["zlib"].libs[0])

        contents += "\nusing bzip2 : {} : <include>{} <search>{} <name>{} ;" \
                    "".format(self.bzip_version,
                              self.deps_cpp_info["bzip2"].include_paths[
                                  0].replace('\\', '/'),
                              self.deps_cpp_info["bzip2"].lib_paths[0].replace(
                                  '\\', '/'),
                              self.deps_cpp_info["bzip2"].libs[0])

        contents += "\nusing python : {} : \"{}\" ;".format(
            sys.version[:3], sys.executable.replace('\\', '/'))

        contents += " : \n"
        if "AR" in os.environ:
            contents += '<archiver>"{}" '.format(which(
                os.environ["AR"]).replace("\\", "/"))
        if "RANLIB" in os.environ:
            contents += '<ranlib>"{}" '.format(which(
                os.environ["RANLIB"]).replace("\\", "/"))
        if "CXXFLAGS" in os.environ:
            contents += '<cxxflags>"{}" '.format(os.environ["CXXFLAGS"])
        if "CFLAGS" in os.environ:
            contents += '<cflags>"{}" '.format(os.environ["CFLAGS"])
        if "LDFLAGS" in os.environ:
            contents += '<linkflags>"{}" '.format(os.environ["LDFLAGS"])

        contents += " ;"

        self.output.warn(contents)
        filename = "{}/user-config.jam".format(folder)
        save(filename, contents)

    def bootstrap(self):
        folder = os.path.join(self.source_folder, self.folder_name, "tools",
                              "build")
        bootstrap = "./bootstrap.sh"
        self.output.info(
            f"Using {self.settings.compiler} "
            f"{self.settings.compiler.version}")
        with chdir(folder):
            self.output.info(bootstrap)
            self.run(bootstrap)

        return os.path.join(folder, "b2")

    def package(self):
        out_lib_dir = os.path.join(self.folder_name, "stage", "lib")
        self.copy(pattern="*", dst="include/boost",
                  src=f"{self.folder_name}/boost")
        if not self.options.shared:
            self.copy(pattern="*.a", dst="lib", src=out_lib_dir,
                      keep_path=False)

        self.renames_to_make_cmake_find_package_happy()

    def renames_to_make_cmake_find_package_happy(self):
        if not self.options.skip_lib_rename:

            renames = []
            for libname in os.listdir(
                    os.path.join(self.package_folder, "lib")):
                new_name = libname
                libpath = os.path.join(self.package_folder, "lib", libname)
                if "-" in libname:
                    new_name = libname.split("-", 1)[0] + "." + \
                               libname.split(".")[-1]
                    if new_name.startswith("lib"):
                        new_name = new_name[3:]
                renames.append([libpath,
                                os.path.join(self.package_folder, "lib",
                                             new_name)])

            for original, new in renames:
                if original != new and not os.path.exists(new):
                    self.output.info("Rename: %s => %s" % (original, new))
                    os.rename(original, new)

    def package_info(self):
        gen_libs = collect_libs(self)

        ordered_libs = [[] for _ in range(len(self.lib_list))]

        missing_order_info = []
        for real_lib_name in gen_libs:
            for pos, alib in enumerate(self.lib_list):
                if os.path.splitext(real_lib_name)[0].split("-")[0].endswith(
                        alib):
                    ordered_libs[pos].append(real_lib_name)
                    break
            else:
                if "_exec_monitor" not in real_lib_name:
                    missing_order_info.append(real_lib_name)

        # Flat the list and append the missing order
        self.cpp_info.libs = [item for sublist in ordered_libs
                              for item in sublist if
                              sublist] + missing_order_info

        self.output.info("LIBRARIES: %s" % self.cpp_info.libs)
        self.output.info("Package folder: %s" % self.package_folder)

        if not self.options.shared:
            self.cpp_info.defines.append("BOOST_ALL_DYN_LINK")
        else:
            self.cpp_info.defines.append("BOOST_USE_STATIC_LIBS")

        if not self.options.without_python:
            if not self.options.shared:
                self.cpp_info.defines.append("BOOST_PYTHON_STATIC_LIB")

        self.cpp_info.libs.append("pthread")

        self.env_info.BOOST_ROOT = self.package_folder
