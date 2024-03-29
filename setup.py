#!/usr/bin/env python

from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'requirements.txt'), encoding='utf-8') as f:
    requirements = f.readlines()
	
# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
	long_description = f.read()

setup(name='spans_and_trees',

	version='0.1.4',

	description='Convert between XML trees and span representation',
	
	long_description=long_description,
	long_description_content_type='text/markdown',

	url='https://github.com/jakelever/spans_and_trees',
	
	author='Jake Lever',
	author_email='jake.lever@gmail.com',
	
	license='MIT',

	classifiers=[
		# How mature is this project? Common values are
		#   3 - Alpha
		#   4 - Beta
		#   5 - Production/Stable
		'Development Status :: 4 - Beta',

		# Indicate who your project is intended for
		'Intended Audience :: Developers',

		# Pick your license as you wish (should match "license" above)
		'License :: OSI Approved :: MIT License',

		# Specify the Python versions you support here. In particular, ensure
		# that you indicate whether you support Python 2, Python 3 or both.
		'Programming Language :: Python :: 3.8',
	],

	keywords='xml',
	
	packages=['spans_and_trees'],
	
	install_requires=requirements,

	scripts=[]
	)

