#!/usr/bin/env python

import os
from setuptools import setup


here = os.path.abspath(os.path.dirname(__file__))

packages = ['atlasplots']

requires = [
    'numpy>=1.18',
]

about = {}
with open(os.path.join(here, 'atlasplots', '__version__.py'), 'r') as f:
    exec(f.read(), about)

# The text of the README file
with open(os.path.join(here, 'README.md'), 'r') as f:
    readme = f.read()


setup(
    name=about['__title__'],
    version=about['__version__'],
    description=about['__description__'],
    long_description=readme,
    long_description_content_type="text/markdown",
    author=about['__author__'],
    author_email=about['__author_email__'],
    url=about['__url__'],
    packages=packages,
    package_data={'': ['LICENSE', 'NOTICE'], 'atlasplots': ['*.pem']},
    package_dir={'atlasplots': 'atlasplots'},
    include_package_data=True,
    python_requires=">=3.6.*",
    install_requires=requires,
    license=about['__license__'],
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: CPython',
    ],
    project_urls={
        'Documentation': 'https://atlas-plots.readthedocs.io/',
        'Source': 'https://github.com/joeycarter/atlas-plots/',
    },
)
