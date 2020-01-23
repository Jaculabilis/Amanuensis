from setuptools import setup, find_packages

setup(
	name='amanuensis',
	version='0.0.1',
	packages=find_packages(),
	include_package_data=True,
	zip_safe=True,
	install_requires=[
		'flask',
		'flask_wtf',
		'flask_login',
	],
)