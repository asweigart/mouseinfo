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
    install_requires=['pyobjc-core;platform_system=="Darwin"',
                      'pyobjc-framework-quartz;platform_system=="Darwin"',
                      'python-Xlib;platform_system=="Linux"',
                      'pyperclip',
                      'Pillow >= 6.2.1; python_version == "3.8"',
                      'Pillow >= 5.2.0; python_version == "3.7"',
                      'Pillow >= 4.0.0; python_version == "3.6"',
                      'Pillow >= 3.2.0; python_version == "3.5"',
                      'Pillow <= 5.4.1, >= 2.5.0; python_version == "3.4"',
                      'Pillow <= 4.3.0, >= 2.0.0; python_version == "3.3"',
                      'Pillow <= 3.4.2, >= 2.0.0; python_version == "3.2"',
                      'Pillow >= 2.0.0; python_version == "2.7"',
                      ],
    keywords='',
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
)
