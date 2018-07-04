from setuptools import setup, find_packages
from pathlib import Path

here = Path(__file__).resolve().parent
with (here / 'sanajeh' / 'VERSION').open() as f:
    VERSION = f.read().strip('\n')

with (here / 'README.rst').open(encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='sanajeh',
    version=VERSION,
    description='Simulate fMRI and iEEG data in BIDS format',
    long_description=long_description,
    url='https://github.com/gpiantoni/sanajeh',
    author="Gio Piantoni",
    author_email='sanajeh@gpiantoni.com',
    license='MIT',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Healthcare Industry',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Scientific/Engineering :: Medical Science Apps.',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        ],
    keywords='bids',
    packages=find_packages(exclude=('tests', )),
    install_requires=[
        'bidso',
        'nibabel',
        'wonambi',
        'popeye',
        ],
    extras_require={
        'test': [  # to run tests
            'pytest',
            'pytest-cov',
            'codecov',
            ],
        },
    package_data={
        'sanajeh': [
            'VERSION',
            'data/electrodes.tsv',
            'data/anat/T1.mgz',
            'data/anat/aparc.a2009s+aseg.mgz',
            ],
    },
    )
