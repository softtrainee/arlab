import os
from setuptools import setup, find_packages

def read(fname):
    root = os.path.dirname(__file__)
    return open(os.path.join(root, fname)).read()

def read_version_file():
    root = os.getcwd()
    p = os.path.join(root, 'version_info.txt')
    with open(p, 'r') as f:
        lines = [l.strip() for l in f]
    return lines

def get_version():
    lines = read_version_file()
    major = lines[1].split('=')[1]
    minor = lines[2].split('=')[1]
    return '.'.join((major, minor))

def get_name():
    lines = read_version_file()
    return lines[0]

AUTHOR = 'Jake Ross'
AUTHOR_EMAIL = 'jirhiker@gmail.com'
DESCRIPTION = 'Extraction Line Controller'
LICENSE = 'GNU'
URL = 'http://code.google.com/p/arlab'


#python setup.py sdist adds everything under version control
setup(

    packages = find_packages(),

    #info
    author = AUTHOR,
    author_email = AUTHOR_EMAIL,
    description = DESCRIPTION,
    long_description = read('README'),
    license = LICENSE,
    url = URL,
    name = get_name(),
    version = get_version()
    )


