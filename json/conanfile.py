import os

from conans import ConanFile
from conans.tools import download, check_sha256


class NlohmannJsonConan(ConanFile):
    name = "json"
    with open(os.path.join(os.path.dirname(os.path.realpath(
            __file__)), "VERSION.txt"), 'r') as version_file:
        version = version_file.read()
    settings = {}
    description = "JSON for Modern C++"
    generators = "cmake", "virtualenv"
    exports = "VERSION.txt"

    url = "https://github.com/nlohmann/json"
    license = "https://github.com/nlohmann/json/blob/v2.1.0/LICENSE.MIT"

    options = {'no_exceptions': [True, False]}
    default_options = 'no_exceptions=False'

    def config(self):
        self.options.remove("os")
        self.options.remove("compiler")
        self.options.remove("shared")
        self.options.remove("build_type")
        self.options.remove("arch")

    def source(self):
        download_url = 'https://github.com/nlohmann/json/releases/' \
                       'download/v{!s}/json.hpp'.format(self.version)
        download(download_url, 'json.hpp')
        check_sha256('json.hpp',
                     'a571dee92515b685784fd527e38405cf3f5e13e96edbfe3f03d6df2e'
                     '363a767b')

    def build(self):
        return  # Nothing to do. Header Only

    def package(self):
        self.copy(pattern='json.hpp', dst='include/nlohmann', src=".")

    def package_info(self):
        if self.options.no_exceptions:
            self.cpp_info.defines.append('JSON_NOEXCEPTION=1')
        self.cpp_info.includedirs = ['include']
        self.env_info.CPATH.append("{}/include".format(self.package_folder))
