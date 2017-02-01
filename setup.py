import os
from setuptools import find_packages, setup
import csdn
with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
	README = readme.read()
with open('requirements.txt') as f:
	required = f.read().splitlines()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
	name = 'csdn',
	version = csdn.__version__,
	install_requires = required,
	packages = find_packages(),
	entry_points = {
        'console_scripts' : ['csdn=csdn.__main__:cli',
                             ],
    },
	include_package_data = True,
	license = 'BSD License', 
	description = 'csdn blog backup or offline.',
	long_description = README,
	url = 'https://github.com/minghu6/csdn',
	author = 'minghu6',
	author_email = 'a19678zy@163.com',
	classifiers=[
		'Intended Audience :: Developers',
		'License :: OSI Approved :: BSD License',
		'Operating System :: OS Independent',
		'Programming Language :: Python',
		'Programming Language :: Python :: 3',
	],
	)
