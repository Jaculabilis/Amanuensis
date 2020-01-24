from setuptools import setup, find_packages

with open("README.md") as f:
	long_desc = f.read()

setup(
	name='amanuensis',
	version='0.0.1',
	author='Tim Van Baak',
	description='An application for playing Lexicon, the encyclopedia RPG',
	long_description=long_desc,
	long_description_content_type='text/markdown',
	url='https://github.com/Jaculabilis/Amanuensis',
	packages=find_packages(),
	include_package_data=True,
	zip_safe=True,
	install_requires=[
		'flask',
		'flask_wtf',
		'flask_login',
	],
)