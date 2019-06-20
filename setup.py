import re, io
from setuptools import setup, find_packages

# Load version from module (without loading the whole module)
with open('src/mouseinfo/__init__.py', 'r') as fo:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fo.read(), re.MULTILINE).group(1)

# Read in the README.md for the long description.
with io.open('README.md', encoding='utf-8') as fo:
    long_description = fo.read()

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
    install_requires=['pyobjc-core;platform_system=="Darwin"', 'pyobjc;platform_system=="Darwin"',
                      'python3-Xlib;platform_system=="Linux" and python_version>="3.0"', 'Xlib;platform_system=="Linux" and python_version<"3.0"',
                      'Pillow', 'pyperclip'],
    keywords='',
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8'
    ],
)
