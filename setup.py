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
        'cldfbench',
    ],
    extras_require={
        'test': [
            'pytest-cldf',
        ],
    },
)
