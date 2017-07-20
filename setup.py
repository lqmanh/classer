from setuptools import find_packages, setup

setup(
    name='classer',
    version='1.0',
    author='Luong Quang Manh',
    license='MIT',
    install_requires=['click', 'pendulum', 'hjson'],
    packages=find_packages(exclude=['tests']),
    entry_points={
        'console_scripts': ['classer=classer.main:cli'],
    }
)
