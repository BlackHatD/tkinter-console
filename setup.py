# -*- coding:utf-8 -*-
import os
import codecs
from setuptools import setup, find_packages

#======================================================================#
# User definitions
#======================================================================#
# package
package_name         = 'tkinter_console'

# version
version_py_file      = None     # 'version.py'
__version__          = '0.0.1'

# others
url                  = 'https://github.com/BlackHatD/tkinter-console'
author               = 'BlackHatD'
author_email         = ''
description          = 'tkinter console'
keywords             = []

LICENSE              = 'The GNU GENERAL PUBLIC LICENSE Version 2'

zip_safe             = False
include_package_data = True

command_name = package_name
entry_points = {}
#entry_points = {
#    'console_scripts': [
#        '{command_name} = {package_name}.cli:main'.format(command_name=command_name, package_name=package_name)
#    ]
#}


#======================================================================#
# Developer definitions
#======================================================================#
here = os.path.abspath(os.path.dirname(__file__))

class PackageNotFoundError(ImportError):
    """ Package not found. """
    def __init__(self, *args, **kwargs):
        pass

# check package
if not os.path.exists(os.path.join(here, package_name)):
    raise PackageNotFoundError('"[!!] {} does not exists!"'.format(package_name))

# read README.md
with codecs.open(os.path.join(here, 'README.md'), encoding='utf-8') as fh:
    long_description = '\n' + fh.read()

# get version from version.py
if version_py_file:
    with open(os.path.join(here, package_name, version_py_file)) as fp:
        exec(fp.read())


setup(
    name=package_name
    , version=__version__
    , author=author
    , author_email=author_email
    , url=url
    , license=LICENSE
    , packages=find_packages(
        include=['{package_name}'.format(package_name=package_name)
                 , '{package_name}.*'.format(package_name=package_name)]
    )
    , include_package_data=include_package_data
    , package_data={'': ['LICENSE']}
    , description=description
    , long_description_content_type='text/markdown'
    , long_description=long_description
    , zip_safe=zip_safe
    , entry_points=entry_points
    #, install_requires=open('requirements.txt').read().splitlines()
    , keywords=keywords
)
