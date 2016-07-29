from setuptools import setup, find_packages

version = '0.2.0'

REQUIREMENTS = [
    'lxml',
    'requests'
]

setup(
    name='python-amazon-aws',
    version=version,
    packages=find_packages(),
    url='https://github.com/ziplokk1/python-amazon-aws',
    license='LICENSE.txt',
    author='Mark Sanders',
    author_email='sdscdeveloper@gmail.com',
    install_requires=REQUIREMENTS,
    description='Wrapper and parser modules for amazon\'s AWS API.',
    include_package_data=True
)
