# ********************************************************** #
#     ___  ________    ___   _____    _____ __        __     #
#    /   |/_  __/ /   /   | / ___/   / ___// /___  __/ /__   #
#   / /| | / / / /   / /| | \__ \    \__ \/ __/ / / / / _ \  #
#  / ___ |/ / / /___/ ___ |___/ /   ___/ / /_/ /_/ / /  __/  #
# /_/  |_/_/ /_____/_/  |_/____/   /____/\__/\__, /_/\___/   #
#                                           /____/           #
# ********************************************************** #

"""
atlasplots.atlasstyle
~~~~~~~~~~~~~~~~~~~~~

Python implementation of the ATLAS PubCom style guide for plots in ROOT:

    https://twiki.cern.ch/twiki/bin/view/AtlasProtected/PubComPlotStyle

This implementation uses ROOT fonts with precision = 3, where text sizes are
given in pixels. Using text sizes in pixels is useful for canvases with
multiple TPads of different sizes, as the text size will not depend on the
dimensions of the pad. The default font used by the ATLAS style is Arial (ROOT
font 43).

For general instructions on formatting text in ROOT, refer to,

    https://root.cern.ch/doc/master/classTAttText.html

Examples
--------

>>> import ROOT
>>> import atlasplots as aplt
>>> aplt.set_atlas_style()
>>> canv = ROOT.TCanvas("canv", "", 600, 600)
>>> ROOT.gPad.DrawFrame(0,0,1,1)
>>> aplt.atlas_label(text="Internal", loc='upper left');

:copyright: (c) 2020-2021 Joey Carter.
:license: MIT, see :ref:`LICENSE <license>` for more details.
"""

import ROOT as root


def atlas_style(tsize=29):
    """Defines the "official" ATLAS plot style.

    Parameters
    ----------
    tsize : float, optional
        Text size in pixels (default: 29).

    Returns
    -------
    ROOT.TStyle
        The TStyle object defining the ATLAS Style.
    """
    atlasStyle = root.TStyle("ATLAS", "Atlas Style")

    # Use plain black on white colors
    icol = 0  # White
    atlasStyle.SetFrameBorderMode(icol)
    atlasStyle.SetFrameFillColor(icol)
    atlasStyle.SetCanvasBorderMode(icol)
    atlasStyle.SetCanvasColor(icol)
    atlasStyle.SetPadBorderMode(icol)
    atlasStyle.SetPadBorderSize(icol)
    atlasStyle.SetPadColor(icol)
    atlasStyle.SetStatColor(icol)

    # Set the paper & margin sizes
    atlasStyle.SetPaperSize(20, 26)

    # Set margin sizes
    atlasStyle.SetPadTopMargin(0.05)
    atlasStyle.SetPadRightMargin(0.05)
    atlasStyle.SetPadBottomMargin(0.16)
    atlasStyle.SetPadLeftMargin(0.16)

    # Set title offsets (for axis labels)
    atlasStyle.SetTitleXOffset(1.4)
    atlasStyle.SetTitleYOffset(1.4)

    # Set font
    font = 43  # Arial

    atlasStyle.SetTextFont(font)
    atlasStyle.SetTextSize(tsize)

    atlasStyle.SetLabelFont(font, "x")
    atlasStyle.SetTitleFont(font, "x")
    atlasStyle.SetLabelFont(font, "y")
    atlasStyle.SetTitleFont(font, "y")
    atlasStyle.SetLabelFont(font, "z")
    atlasStyle.SetTitleFont(font, "z")

    atlasStyle.SetLabelSize(tsize, "x")
    atlasStyle.SetTitleSize(tsize, "x")
    atlasStyle.SetLabelSize(tsize, "y")
    atlasStyle.SetTitleSize(tsize, "y")
    atlasStyle.SetLabelSize(tsize, "z")
    atlasStyle.SetTitleSize(tsize, "z")

    # Use bold lines and markers
    atlasStyle.SetMarkerStyle(20)
    atlasStyle.SetMarkerSize(1.2)
    atlasStyle.SetHistLineWidth(2)
    atlasStyle.SetLineStyleString(2, "[12 12]") # postscript dashes

    # Get rid of error bar caps
    atlasStyle.SetEndErrorSize(0.)

    # Do not display any of the standard histogram decorations
    atlasStyle.SetOptTitle(0)
    atlasStyle.SetOptStat(0)
    atlasStyle.SetOptFit(0)

    # Put tick marks on top and RHS of plots
    atlasStyle.SetPadTickX(1)
    atlasStyle.SetPadTickY(1)

    # Remove legend borders and set font
    atlasStyle.SetLegendBorderSize(0)
    atlasStyle.SetLegendFillColor(0)
    atlasStyle.SetLegendFont(43)
    atlasStyle.SetLegendTextSize(tsize)

    return atlasStyle
