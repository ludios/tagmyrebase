#!/usr/bin/env python3

from setuptools import setup

setup(
	name="tagmyrebase",
	version="4.1.0",
	description="Utility to tag HEAD and the upstream commit after a rebase",
	python_requires=">=3.10",
	scripts=["tagmyrebase"],
)
