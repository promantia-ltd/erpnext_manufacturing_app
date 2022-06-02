from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in manufacturer_customizations/__init__.py
from manufacturer_customizations import __version__ as version

setup(
	name="manufacturer_customizations",
	version=version,
	description="manufacturer_customizations",
	author="manufacturer_customizations",
	author_email="abc@gmail.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
