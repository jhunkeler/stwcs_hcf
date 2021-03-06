#!/usr/bin/env python
import os
import subprocess
import sys
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

if os.path.exists('relic'):
    sys.path.insert(1, 'relic')
    import relic.release
else:
    try:
        import relic.release
    except ImportError:
        try:
            subprocess.check_call(['git', 'clone',
                'https://github.com/jhunkeler/relic.git'])
            sys.path.insert(1, 'relic')
            import relic.release
        except subprocess.CalledProcessError as e:
            print(e)
            exit(1)


version = relic.release.get_info()
relic.release.write_template(version, 'stwcs')
 
try:
    from distutils.config import ConfigParser
except ImportError:
    from configparser import ConfigParser

conf = ConfigParser()
conf.read(['setup.cfg'])

# Get some config values                                                                   
metadata = dict(conf.items('metadata'))
PACKAGENAME = metadata.get('package_name', 'stwcs')
DESCRIPTION = metadata.get('description', '')
AUTHOR = metadata.get('author', 'STScI')
AUTHOR_EMAIL = metadata.get('author_email', 'help@stsci.edu')

class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ['stwcs/tests']
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded                                
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)

setup(
    name = PACKAGENAME,
    version = version.pep386,
    author = AUTHOR,
    author_email = AUTHOR_EMAIL,
    description = DESCRIPTION,
    url = 'https://github.com/spacetelescope/stwcs',
    classifiers = [
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering :: Astronomy',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    install_requires = [
        'astropy',
        'numpy',
        'stsci.tools',
    ],
    packages = find_packages(),
    tests_require = ['pytest'],
    package_data = {
        'stwcs/gui': ['*.help'],
        'stwcs/gui/pars': ['*'],
        'stwcs/gui/htmlhelp': ['*'],
    },
    cmdclass = {"test": PyTest}
)
