from setuptools import setup


setup(
    name='cldfbench_wals',
    py_modules=['cldfbench_wals'],
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
        'python-nexus',
        'newick',
        'cldfbench>=1.6.0',
        'clldutils>=3.7.0',
        'pycldf>=1.19.0',
        'pybtex>=0.24.0',
        'beautifulsoup4>=4.9.3',
        'csvw>=1.10.1',
    ],
    extras_require={
        'test': [
            'pytest-cldf',
        ],
    },
)
