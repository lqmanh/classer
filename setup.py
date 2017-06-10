from setuptools import setup, find_packages


setup(
    name='classer',
    version='0.9',
    author='Luong Quang Manh',
    license='MIT',
    install_requires=['click', 'pendulum', 'hjson'],
    packages=find_packages(exclude=('tests',)),
    entry_points={
        'console_scripts': ['classer=sample.main:cli'],
    }
)
