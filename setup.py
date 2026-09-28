from setuptools import setup


setup(
    name='cldfbench_wals',
    py_modules=['cldfbench_wals'],
    packages=['walscommands'],
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'cldfbench.dataset': [
            'wals=cldfbench_wals:Dataset',
        ],
        'cldfbench.commands': [
            'wals=walscommands',
        ],
    },
    install_requires=[
        'pyglottolog',
        'python-nexus',
        'newick',
        'cldfbench>=2',
        'clldutils>=4',
        'pycldf>=2',
        'simplepybtex',
        'beautifulsoup4>=4.9.3',
        'csvw>=1.10.1',
        'unidecode',
        'pycountry',
    ],
    extras_require={
        'test': [
            'pytest-cldf',
        ],
    },
)
