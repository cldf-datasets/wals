"""
It turns out that the data we have for Bira is actually for two separate languages
(the two with the two ISO codes bip and brf), so this needs to be split into two languages,
Bila and Bera.

We should keep the WALS code bia for Bila [bip], changing the name from Bira to Bila, and add a new language for Bera, for which we could use the WALS code brq.

The data points that use Kutsch Lojenga 2003 as the source should go with Bila, those that use Meinhof 1938/39 should go with Bera.
"""
from csvw import dsv

from cldfbench_wals import Dataset


def register(parser):
    pass


def run(args):
    ds = Dataset()

