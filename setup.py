# -*- coding: utf-8 -*-
import setuptools
from os.path import join, dirname

from setuptools.command.test import test as TestCommand
import sys

class Tox(TestCommand):

    user_options = TestCommand.user_options + [
        ('environment=', 'e', "Run 'test_suite' in specified environment")
    ]
    environment = None

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import tox
        if self.environment:
            self.test_args.append('-e{0}'.format(self.environment))
        errno = tox.cmdline(self.test_args)
        sys.exit(errno)

setuptools.setup(
    name="python-passaporte-web",
    version="0.2",
    packages=["passaporte_web"],
    include_package_data=True,  # declarations in MANIFEST.in
    install_requires=open(join(dirname(__file__), 'requirements.txt')).readlines(),
    tests_require=['tox', 'virtualenv==1.10.1'],
    cmdclass = {'test': Tox},
    test_suite='passaporte_web.tests',
    author="vitormazzi",
    author_email="vitormazzi@gmail.com",
    url="http://github.com/myfreecomm/python-passaporte-web",
    license="Apache 2.0",
    description="Python client app for Passaporte Web.",
    long_description=open(join(dirname(__file__), "README.rst")).read(),
    keywords="python passaporteweb",
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Topic :: Software Development',
    ],
)
