from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in sydani/__init__.py
from sydani import __version__ as version

setup(
	name="sydani",
	version=version,
	description="For Sydani custom apps",
	author="ekomobong",
	author_email="erp@sydani.org",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
