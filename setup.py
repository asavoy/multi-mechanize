#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
	name = "multi-mechanize",
        packages = find_packages(),
        package_data = {"multi_mechanize": ["lib/templates/*"]},
        zip_safe = False,
        version = "1.010",
	description = "Multi-Mechanize is an open source framework for API performance and load testing.",
	author = "Corey Goldberg",
	author_email = "",
	url = "http://code.google.com/p/multi-mechanize/",
	download_url = "https://github.com/asavoy/multi-mechanize",
	install_requires = ['Jinja2', 'matplotlib', 'mechanize'],
	keywords = ["mechanize", "load-testing"],
        scripts = ["multi_mechanize/multi-mechanize.py"],
        classifiers = [
		"Programming Language :: Python",
		"Development Status :: 3 - Alpha",
		"Natural Language :: English",
		"Environment :: Web Environment",
		"Intended Audience :: Developers",
		"Operating System :: OS Independent",
		"Topic :: Utilities"
		],
)

