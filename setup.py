from setuptools import setup, find_packages

version = '0.0.0dev'

setup(
    name = 'isotoma.zope.groupreadableblobstorage',
    version = version,
    description = "Make blob storage group readable",
    package_data = {
        '': ['README.rst', ],
    },
    packages = find_packages(exclude=['ez_setup']),
    namespace_packages = ['isotoma', 'isotoma.zope'],
    include_package_data = True,
    zip_safe = False,
    install_requires = [
        'setuptools',
    ],
)
