# ********************************************************** #
#     ___  ________    ___   _____    ____  __      __       #
#    /   |/_  __/ /   /   | / ___/   / __ \/ /___  / /______ #
#   / /| | / / / /   / /| | \__ \   / /_/ / / __ \/ __/ ___/ #
#  / ___ |/ / / /___/ ___ |___/ /  / ____/ / /_/ / /_(__  )  #
# /_/  |_/_/ /_____/_/  |_/____/  /_/   /_/\____/\__/____/   #
#                                                            #
# ********************************************************** #

"""
ATLAS Plots
===========

**ATLAS Plots** provides a simple interface to produce plots in ROOT following
the standard ATLAS style guidelines.

Basic usage:

>>> import atlasplots as aplt
>>> aplt.set_atlas_style()
>>> fig = aplt.figure()
>>> fig.show()

:copyright: (c) 2020-2021 Joey Carter.
:license: MIT, see LICENSE for more details.
"""

from .__version__ import (
    __title__,
    __description__,
    __url__,
    __version__,
    __author__,
    __author_email__,
    __license__,
    __copyright__,
)

import ROOT as root
root.PyConfig.IgnoreCommandLineOptions = True  # Stops ROOT from hijacking --help

from .api import (
    set_atlas_style,
    figure,
    subplots,
    ratio_plot,
    atlas_label,
)
