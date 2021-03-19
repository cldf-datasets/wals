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
        'cldfbench>=1.3.0',
        'clldutils>=3.6.0',
        'pycldf>=1.17.0',
        'pybtex>=0.23.0',
        'bs4>=4.9.1',
    ],
    extras_require={
        'test': [
            'pytest-cldf',
        ],
    },
)
