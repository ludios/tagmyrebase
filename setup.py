#!/usr/bin/env python3

from distutils.core import setup

setup(
	name="tagmyrebase",
	version="3.1.0",
	description="Utility to tag HEAD and the upstream commit after a rebase",
	scripts=["tagmyrebase"],
)
