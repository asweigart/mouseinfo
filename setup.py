import io
import os
import re
from setuptools import setup, find_packages

scriptFolder = os.path.dirname(os.path.realpath(__file__))
os.chdir(scriptFolder)

# Find version info from module (without importing the module):
with open('src/mouseinfo/__init__.py', 'r') as fileObj:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fileObj.read(), re.MULTILINE).group(1)

# Use the README.md content for the long description:
readmeFilename = os.path.join(scriptFolder, 'README.md')
with io.open(readmeFilename, encoding='utf-8') as fileObj:
    long_description = fileObj.read()

setup(
    name='MouseInfo',
    version=version,
    url='https://github.com/asweigart/mouseinfo',
    author='Al Sweigart',
    author_email='al@inventwithpython.com',
    description=('''An application to display XY position and RGB color information for the pixel currently under the mouse. Works on Python 2 and 3.'''),
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='GPLv3+',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    test_suite='tests',
    # NOTE: Update the python_version info for Pillow as Pillow supports later versions of Python.
    install_requires=['pyobjc-core;platform_system=="Darwin"', 'pyobjc;platform_system=="Darwin"',
                      'python3-Xlib;platform_system=="Linux" and python_version>="3.0"', 'Xlib;platform_system=="Linux" and python_version<"3.0"',
                      'Pillow;python_version=="2.7" or python_version>="3.5" and python_version<="3.7"', 'pyperclip'],
    keywords='',
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)
