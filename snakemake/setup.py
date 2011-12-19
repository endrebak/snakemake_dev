# coding: utf-8
from distutils.core import setup, Extension
import sys

if sys.version_info < (3,0):
    sys.stdout.write("At least Python 3 is required.\n")
    sys.exit(1)
    
setup(
    name = 'snakemake',
    version = "0.1",
    author = 'Johannes Köster',
    author_email = 'johannes.koester@tu-dortmund.de',
    description = 'Build systems like make are frequently used to create complicated workflows, e.g. in bioninformatics. This project aims to reduce the complexity of creating workflows by providing a clean and modern domain specific language (DSL) in python style, together with a fast and comfortable execution environment.',
    license = 'MIT',
    #package_dir = {'': 'lib'},
    packages = ['snakemake'],
    scripts = ['bin/snakemake'],
    classifiers = [
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        #"Operating System :: POSIX",
        "Topic :: Scientific/Engineering :: Bio-Informatics"
    ]
)