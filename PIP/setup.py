from setuptools import setup, find_packages


setup(
	name='foresteam_cmdargparse',
	version='1.0',
	license='MIT',
	author="Foresteam",
	author_email='heler1141@gmail.com',
	packages=find_packages('src'),
	package_dir={'': 'src'},
	url='https://github.com/Foresteam/cmd-argparse',
	keywords='command parsing discord',
	install_requires=[
		'discord',
	]
)