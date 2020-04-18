import os
from conans import ConanFile


class LocalGccConan(ConanFile):
    name = "gcc"
    description = "Locally installed GCC"
    with open(os.path.join(os.path.dirname(os.path.realpath(
            __file__)), "VERSION.txt"), 'r') as version_file:
        version = version_file.read()
    license = "GNU"
    url = "https://www.gnu.org/software/gcc/"
    settings = {
        "os": ["Linux"],
        "arch": ["x86_64"]}
    generators = "virtualenv"
    exports = "VERSION.txt"

    gcc_dir = os.path.expanduser('~/local/gcc{}'.format(
        version.replace(".", ""))).strip("\n")

    def build(self):
        print(self.gcc_dir)
        os.listdir(self.gcc_dir)
        self.settings.remove("build_type")
        self.settings.remove("compiler")

    def package(self):
        self.output.info('Generating package from {}'.format(self.gcc_dir))
        self.copy('*', src=self.gcc_dir, dst="")

    def package_info(self):
        self.env_info.LD_LIBRARY_PATH.append(
            os.path.join(self.package_folder, 'lib64'))
        self.env_info.PATH.append(os.path.join(self.package_folder, 'bin'))
        self.env_info.CC = os.path.join(self.package_folder, 'bin', 'gcc')
        self.env_info.CXX = os.path.join(self.package_folder, 'bin', 'g++')
        self.cpp_info.libdirs = ['lib64']
