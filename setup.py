import sys
from setuptools import setup

if sys.version_info < (3, 6):
    sys.exit('Sorry, Python lower than 3.0 is not supported')

setup(
    name = "twkbpy",
    version = "0.1",
    author = "DCA",
    author_email = "kevin@ank.com",
    description = ("TWKB GIS Loader in pure python"),
    license = "MIT",
    keywords = "",
    url = "https://github.com/kevinsmathers-pge/twkbpy",
    packages = ['twkbpy'],
    classifiers = [],
    install_requires = [

    ]
)
