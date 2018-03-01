## -*- encoding: utf-8 -*-
import os
import sys
import re
from setuptools import setup
from codecs import open # To open the README file with proper encoding
from setuptools.command.test import test as TestCommand # for tests
from distutils.command import build as build_module

# Get information from separate files (README, VERSION)
def readfile(filename):
    with open(filename,  encoding='utf-8') as f:
        return f.read()

# Check the right Sage version
class build(build_module.build):
    def run(self):
        from sagemath.check_version import check_version
        check_version(sage_required_version)
        build_module.build.run(self)


# For the tests
class SageTest(TestCommand):
    def run_tests(self):
        errno = os.system("sage -t --force-lib uhw_modules uhw_modules/*.pyx")
        if errno != 0:
            sys.exit(1)

if __name__ == "__main__":

    # The next block is needed if there are cython files
    from setuptools import Extension
    from Cython.Build import cythonize
    import Cython.Compiler.Options
    from sage.env import sage_include_directories

    # Cython modules
    ext_modules = [
             Extension('uhw_modules.one_cython_file',
             sources = [os.path.join('uhw_modules','one_cython_file.pyx')],
             include_dirs=sage_include_directories())
    ]

    # Specify the required Sage version
    sage_required_version = '>=8.1'
    REQUIREMENTS = [i.strip() for i in open("requirements.txt").readlines() if i[0] != '#']
    CLASSIFIERS = [i.strip() for i in open("classifiers.txt").readlines() if i[0] != '#']

    setup(
        name = "uhw_modules",
        version = readfile("VERSION"), # the VERSION file is shared with the documentation
        description='Calculates nilpotent cohomology of unitarizable highest weight modules using Enright formula.',
        long_description = readfile("README.rst"), # get the long description from the README
        url='https://github.com/vit-tucek/uhw_modules',
        author='Vít Tuček',
        author_email='vit-tucek@users.noreply.github.com', # choose a main contact email
        license="GNU General Public License v3",
        classifiers = CLASSIFIERS,
        keywords = "days93, combinat",
        setup_requires = REQUIREMENTS, # currently useless, see https://www.python.org/dev/peps/pep-0518/
        install_requires = REQUIREMENTS, # This ensures that Sage is installed
        packages = ['uhw_modules'],
        ext_modules = cythonize(ext_modules), # This line is only needed if there are cython files present
        include_package_data = True,
        cmdclass = {'build': build, 'test': SageTest} # adding a special setup command for tests
    )
