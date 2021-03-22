"""
atlasplots.api
~~~~~~~~~~~~~~

This module implements the ATLAS Plots API.

:copyright: (c) 2020-2021 Joey Carter.
:license: MIT, see :ref:`LICENSE <license>` for more details.
"""

from . import core
from .atlasstyle import atlas_style

import ROOT as root


__all__ = [
    "set_atlas_style",
    "figure",
    "subplots",
    "ratio_plot",
    "atlas_label",
]


def set_atlas_style(tsize=None):
    """Sets the global ROOT plot style to the ATLAS Style.

    Parameters
    ----------
    tsize : float, optional
        Text size in pixels. The default is `None`, in which case it will use
        the default text size defined in `AtlasStyle()`.
    """
    print("\u001b[34;1mApplying ATLAS style settings\u001b[0m")

    if tsize is None:
        style = atlas_style()
    else:
        style = atlas_style(tsize)

    # Release ownership, otherwise lost when moved out of scope
    root.SetOwnership(style, False)

    root.gROOT.SetStyle("ATLAS")
    root.gROOT.ForceStyle()


def figure(name="", title="", figsize=None):
    """Create a new figure.

    Parameters
    ----------
    name : str, optional
        Figure (canvas) name.

    title : str, optional
        Figure (canvas) title.

    figsize : (float, float), optional
        Figure (canvas) dimension `(width, height)` in pixels. The default
            dimensions are (800, 600).

    Returns
    -------
    fig : :class:`~.core.Figure`
        The figure.
    """
    return core.Figure(name, title, figsize)


def subplots(nrows=1, ncols=1, width_ratios=None, height_ratios=None, **fig_kw):
    """Create a figure and a set of subplots.

    Parameters
    ----------
    nrows, ncols : int, default: 1
        Number of rows/columns of the subplot grid.

    width_ratios : array-like of length *ncols*, optional
        Defines the relative widths of the columns. Each column gets a
        relative width of ``width_ratios[i] / sum(width_ratios)``.
        If not given, all columns will have the same width.

    height_ratios : array-like of length *nrows*, optional
        Defines the relative heights of the rows. Each column gets a
        relative height of ``height_ratios[i] / sum(height_ratios)``.
        If not given, all rows will have the same height.

    **fig_kw
        All additional keyword arguments are passed to the :func:`.api.figure`
        call.

    Returns
    -------
    fig : :class:`~.core.Figure`
        The figure.

    ax : :class:`~.core.Axes` or array of `Axes`
        *ax* can be either a single `Axes` object or an array of `Axes` objects
        if more than one subplot was created.

        Typical idioms for handling the return value are just like in
        matplotlib::

            # Using the variable ax for a single Axes
            fig, ax = aplt.subplots()

            # Using the variable axs for multiple Axes
            fig, axs = aplt.subplots(2, 2)

            # Using tuple unpacking for multiple Axes
            fig, (ax1, ax2) = aplt.subplots(1, 2)
            fig, ((ax1, ax2), (ax3, ax4)) = aplt.subplots(2, 2)
    """
    fig = figure(**fig_kw)
    axs = fig.subplots(
        nrows=nrows, ncols=ncols, width_ratios=width_ratios, height_ratios=height_ratios
    )

    return fig, axs


def ratio_plot(hspace=0, **fig_kw):
    """An opinionated method to produce a ratio plot, with a main panel to show
    two or more datasets, and a lower panel to show their ratios.

    These settings are optimized for a 800 x 800 px canvas.

    Parameters
    ----------
    hspace : float
        Space between the main panel and ratio panel.

    **fig_kw
        All additional keyword arguments are passed to the :func:`.api.figure`
        call.

    Returns
    -------
    fig : :class:`~.core.Figure`
        The figure.

    ax : Array of :class:`~.core.Axes`
        The axes. The first set of axes should be the main panel, and each
        subsequent set of axes should be the ratio panels.
    """
    hpad1 = 0.63
    hpad2 = 0.37

    fig, (ax1, ax2) = subplots(2, 1, height_ratios=[hpad1, hpad2], **fig_kw)

    # Remove x-axis labels from top frame
    ax1.frame.GetXaxis().SetLabelSize(0)

    # Set margins
    ax1.pad.SetTopMargin(30./504)
    ax1.pad.SetBottomMargin(hspace/2)  # FIXME

    ax2.pad.SetTopMargin(hspace/2)  # FIXME
    ax2.pad.SetBottomMargin(96./296)

    ax1.frame.GetYaxis().SetTitleOffset(1.9)
    ax2.frame.GetYaxis().SetTitleOffset(1.9)
    ax2.frame.GetXaxis().SetTitleOffset(1.4 / 0.37)
    ax2.frame.GetYaxis().SetNdivisions(505)

    return fig, (ax1, ax2)


def atlas_label(
    x=None,
    y=None,
    text="",
    loc="",
    size=None,
    font=None,
    align=None,
    color=None,
    alpha=None,
    angle=None,
):
    """Draws the "official" ATLAS label.

    Guidelines from PubCom:

    An ATLAS label must be present on plots which have been approved by ATLAS:

    - ATLAS: means the plot has been submitted for publication or is in the
      associated approved auxiliary material (i.e. an ATLAS paper, or a
      pre-datataking publication like the CSC notes).
    - ATLAS Preliminary: means the plot has been approved by ATLAS but has not
      appeared in a refereed publication. This is used in particular for CONF
      and PUB notes.
    - ATLAS Work In Progress: used only in student talks at national meetings
      where the student is presenting what is largely her own work. This should
      not be used for internal plots inside ATLAS.
    - ATLAS Internal: for plots shown in internal ATLAS talks (including
      approval talks) or included in draft documents circulated to ATLAS.

    Parameters
    ----------
    x, y : float, optional
        The x- and y-coordinates of the ATLAS label in NDC units [0, 1].

        This x-coordinate is left-aligned and the y-coordinate is top-aligned
        unless the `align` argument is given.

    text : str, optional
        Additional text, e.g. "Internal", "Preliminary", etc. ROOT TLatex syntax
        is supported.

    loc : str, optional
        The location of the legend.

        The strings 'upper left', 'upper right', 'lower left', 'lower right'
        place the legend at the corresponding corner of the axes/figure. This
        option is overridden if the `x` and `y` arguments are provided.

        The default location is 'upper left'.

    size : float, optional
        Text size.

    font : int, optional
        ROOT font code.

    align : int, optional
        ROOT text-alignment code.

    color : int, optional
        ROOT text-color code.

    alpha : float, optional
        Text alpha.

        Not recommended for official ATLAS labels!

    angle : float, optional
        Text angle in degrees.

        Not recommended for official ATLAS labels!

    Returns
    -------
    ROOT.TLatex
        The TLatex object for this label.
    """
    if root.gROOT.GetStyle("ATLAS") == None:
        print("warning: The 'ATLAS' style has not been set")

    label = root.TLatex()
    label.SetNDC()

    if size is not None:
        label.SetTextSize(size)

    if font is not None:
        label.SetTextFont(font)

    if align is not None:
        label.SetTextAlign(align)

    if color is not None and alpha is not None:
        label.SetTextColorAlpha(color, alpha)
    elif color is not None:
        label.SetTextColor(color)

    if angle is not None:
        label.SetTextAngle(angle)

    if font is not None:
        label.SetTextFont(font)

    # Decide on label position
    if x is not None and y is not None:
        # Set location manually
        xpos = x
        ypos = y

    elif loc:
        # Set location automatically from 'loc' argument
        if loc == "upper left":
            label.SetTextAlign(13)
            xpos = root.gPad.GetLeftMargin() + 0.04
            ypos = 1 - root.gPad.GetTopMargin() - 0.04
        elif loc == "upper right":
            label.SetTextAlign(33)
            xpos = 1 - root.gPad.GetRightMargin() - 0.04
            ypos = 1 - root.gPad.GetTopMargin() - 0.04
        elif loc == "lower left":
            label.SetTextAlign(11)
            xpos = root.gPad.GetLeftMargin() + 0.04
            ypos = root.gPad.GetBottomMargin() + 0.04
        elif loc == "lower right":
            label.SetTextAlign(31)
            xpos = 1 - root.gPad.GetRightMargin() - 0.04
            ypos = root.gPad.GetBottomMargin() + 0.04
        else:
            print(
                "warning: unrecognized location '{}'. "
                "Falling back on 'upper left'".format(loc)
            )
            label.SetTextAlign(13)
            xpos = root.gPad.GetLeftMargin() + 0.04
            ypos = 1 - root.gPad.GetTopMargin() - 0.04

    else:
        # User 'upper left' if no position arguments are given
        label.SetTextAlign(13)
        xpos = root.gPad.GetLeftMargin() + 0.04
        ypos = 1 - root.gPad.GetTopMargin() - 0.04

    if not text:
        label.DrawLatex(xpos, ypos, "#bf{#it{ATLAS}}")
    else:
        label.DrawLatex(xpos, ypos, "#bf{#it{ATLAS}} " + text)

    return label
