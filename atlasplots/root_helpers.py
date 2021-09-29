"""
atlasplots.root_helpers
~~~~~~~~~~~~~~~~~~~~~~~

This module contains helper functions for dealing with ROOT objects, especially
histograms and graphs.

:copyright: (c) 2020-2021 Joey Carter.
:license: MIT, see :ref:`LICENSE <license>` for more details.
"""

import warnings

import ROOT as root

import numpy as np


__all__ = [
    "hist_max",
    "hist_min",
    "graph_ymax",
    "graph_ymin",
    "graph_xmax",
    "graph_xmin",
    "multigraph_ymax",
    "multigraph_ymin",
    "multigraph_xmax",
    "multigraph_xmin",
    "hist_to_graph",
    "graph",
    "set_graphics_attributes",
    "get_color_code",
]


# Data types (keys: ROOT types, values: numpy types)
DTYPE_ROOT2NUMPY = dict(C="i1", S="i2", I="i4", L="i8", F="f4", D="f8")


def _setup_hist_to_array(hist):
    """Returns the shape (dimension) and data type of `hist`, which can be used as input
    when creating a numpy array corresponding to the bin contents of this histogram.

    Parameters
    ----------
    hist : ROOT TH1, TH2 or TH3
        The ROOT histogram.

    Returns
    -------
    shape : tuple
        The dimensions of the histogram, as (NbinsX+2, [NbinsY+2, [NbinsZ+2]]). The
        dimensions are NbinsX+2 so that the over- and underflow bins are included.

    dtype : numpy.dtype
        The numpy data type corresponding to the data type of the histogram.

    Raises
    ------
    TypeError
        If `hist` is not a ROOT histogram.
    """
    # Determine dimensionality and shape
    if isinstance(hist, root.TH3):
        shape = (hist.GetNbinsZ() + 2, hist.GetNbinsY() + 2, hist.GetNbinsX() + 2)
    elif isinstance(hist, root.TH2):
        shape = (hist.GetNbinsY() + 2, hist.GetNbinsX() + 2)
    elif isinstance(hist, root.TH1):
        shape = (hist.GetNbinsX() + 2,)
    else:
        raise TypeError(
            f"hist must be an instance of ROOT.TH1, ROOT.TH2 or ROOT.TH3, not {type(hist)}"
        )

    for hist_type in "DFISC":
        if isinstance(hist, getattr(root, f"TArray{hist_type}")):
            break
    else:
        raise AssertionError(
            "hist is somehow an instance of TH[1|2|3] but not TArray[D|F|I|S|C]"
        )

    # Get histogram data type
    dtype = np.dtype(DTYPE_ROOT2NUMPY[hist_type])

    return shape, dtype


def hist_max(hist, include_err=False, include_overflow=False, axis=None):
    """Returns the histogram's maximum bin content (with or without bin errors).

    Parameters
    ----------
    hist : ROOT TH1, TH2 or TH3
        The ROOT histogram.

    include_err : bool, optional
        Include bin errors when searching for the maximum. If True, the returned
        value(s) is ``hist.GetBinContent(i) + hist.GetBinErrorUp(i)``, where ``i`` is
        the index of the maximum bin. By default, bin errors are not included.

    include_overflow : bool, optional
        If True, the over- and underflow bins will be included in the search for the
        maximum bin. These bins are excluded by default.

    axis : None or int or tuple of ints, optional
        Axis or axes along which to operate, as defined in `numpy.amax()`. By default,
        flattened input is used.

    Returns
    -------
    max : numpy.ndarray or scalar
        Maximum of bin contents of `hist`. If `axis` is None, the result is a scalar
        value. If `axis` is given, the result is an array of dimension ``a.ndim - 1``.
    """
    # Get shape and dtype of hist
    shape, dtype = _setup_hist_to_array(hist)

    if not include_err:
        # Do not need bin errors, can fill `array` directly
        array = np.ndarray(shape=shape, dtype=dtype, buffer=hist.GetArray())
    else:
        # Include bin errors, need to loop bin by bin
        array = np.ndarray(shape=shape, dtype=dtype)

        for ibin, _ in np.ndenumerate(array):
            array[ibin] = hist.GetBinContent(*ibin) + hist.GetBinErrorUp(*ibin)

    if not include_overflow:
        # Remove overflow and underflow bins
        array = array[tuple([slice(1, -1) for idim in range(array.ndim)])]

    # Preserve x, y, z -> axis 0, 1, 2 order
    array = np.transpose(array)

    return np.amax(array, axis=axis)


def hist_min(
    hist, include_err=False, include_overflow=False, only_pos=False, axis=None
):
    """Returns the histogram's minimum bin content (with or without bin errors).

    Parameters
    ----------
    hist : ROOT TH1, TH2 or TH3
        The ROOT histogram.

    include_err : bool, optional
        Include bin errors when searching for the minimum. If True, the returned
        value(s) is ``hist.GetBinContent(i) - hist.GetBinErrorLow(i)``, where ``i`` is
        the index of the minimum bin. By default, bin errors are not included.

    include_overflow : bool, optional
        If True, the over- and underflow bins will be included in the search for the
        minimum bin. These bins are excluded by default.

    only_pos : bool, optional
        Only include positive bins when searching for the minimum. All bins are included
        by default.

        This option is useful for setting the y-axis limits when it is in log scale.

    axis : None or int or tuple of ints, optional
        Axis or axes along which to operate, as defined in `numpy.amin()`. By default,
        flattened input is used.

    Returns
    -------
    min : numpy.ndarray or scalar
        Minimum of bin contents of `hist`. If `axis` is None, the result is a scalar
        value. If `axis` is given, the result is an array of dimension ``a.ndim - 1``.
    """
    # Get shape and dtype of hist
    shape, dtype = _setup_hist_to_array(hist)

    if not include_err:
        # Do not need bin errors, can fill `array` directly
        array = np.ndarray(shape=shape, dtype=dtype, buffer=hist.GetArray())
    else:
        # Include bin errors, need to loop bin by bin
        array = np.ndarray(shape=shape, dtype=dtype)

        for ibin, _ in np.ndenumerate(array):
            array[ibin] = hist.GetBinContent(*ibin) - hist.GetBinErrorLow(*ibin)

    if not include_overflow:
        # Remove overflow and underflow bins
        array = array[tuple([slice(1, -1) for idim in range(array.ndim)])]

    if only_pos:
        array = array[array > 0]

    # Preserve x, y, z -> axis 0, 1, 2 order
    array = np.transpose(array)

    return np.amin(array, axis=axis)


def graph_ymax(graph):
    """Returns the graph's maximum y-value, including error bars where relevant.

    Recall that you can always retrieve the maximum *point* y-value of a TGraph object
    with ``ROOT.TMath.MaxElement(gr.GetN(), gr.GetY())``.

    The value returned depends on the type of TGraph given:

    - TGraph: the graphs's maximum ``point`` value.
    - TGraphErrors: the graph's maximum ``point + error`` value.
    - TGraphAsymmErrors: the graph's maximum ``point + error_high`` value.

    Parameters
    ----------
    graph : ROOT TGraph, TGraphErrors or TGraphAsymmErrors
        The ROOT graph object.

    Returns
    -------
    ymax : scalar
        Maximum y-value of graph.
    """
    if isinstance(graph, root.TGraphAsymmErrors):
        array = np.ndarray(
            shape=graph.GetN(), dtype="f8", buffer=graph.GetY()
        ) + np.ndarray(shape=graph.GetN(), dtype="f8", buffer=graph.GetEYhigh())

    elif isinstance(graph, root.TGraphErrors):
        array = np.ndarray(
            shape=graph.GetN(), dtype="f8", buffer=graph.GetY()
        ) + np.ndarray(shape=graph.GetN(), dtype="f8", buffer=graph.GetEY())

    elif isinstance(graph, root.TGraph):
        array = np.ndarray(shape=graph.GetN(), dtype="f8", buffer=graph.GetY())

    else:
        TypeError(
            f"graph must be an instance of ROOT.TGraph, ROOT.TGraphErrors or "
            f"ROOT.TGraphAsymmErrors, not {type(graph)}"
        )

    return np.amax(array)


def graph_ymin(graph, only_pos=False):
    """Returns the graph's minimum y-value, including error bars where relevant.

    Recall that you can always retrieve the minimum *point* y-value of a TGraph object
    with ``ROOT.TMath.MinElement(gr.GetN(), gr.GetY())``.

    The value returned depends on the type of TGraph given:

    - TGraph: the graphs's minimum ``point`` value.
    - TGraphErrors: the graph's minimum ``point - error`` value.
    - TGraphAsymmErrors: the graph's minimum ``point - error_low`` value.

    Parameters
    ----------
    graph : ROOT TGraph, TGraphErrors or TGraphAsymmErrors
        The ROOT graph object.

    only_pos : bool, optional
        Only include positive values when searching for the minimum. All points are
        included by default.

        This option is useful for setting the y-axis limits when it is in log scale.

    Returns
    -------
    ymin : scalar
        Minimum y-value of graph.
    """
    if isinstance(graph, root.TGraphAsymmErrors):
        array = np.ndarray(
            shape=graph.GetN(), dtype="f8", buffer=graph.GetY()
        ) - np.ndarray(shape=graph.GetN(), dtype="f8", buffer=graph.GetEYlow())

    elif isinstance(graph, root.TGraphErrors):
        array = np.ndarray(
            shape=graph.GetN(), dtype="f8", buffer=graph.GetY()
        ) - np.ndarray(shape=graph.GetN(), dtype="f8", buffer=graph.GetEY())

    elif isinstance(graph, root.TGraph):
        array = np.ndarray(shape=graph.GetN(), dtype="f8", buffer=graph.GetY())

    else:
        TypeError(
            f"graph must be an instance of ROOT.TGraph, ROOT.TGraphErrors or "
            f"ROOT.TGraphAsymmErrors, not {type(graph)}"
        )

    if only_pos:
        array = array[array > 0]

    return np.amin(array)


def graph_xmax(graph):
    """Returns the graph's maximum x-value, including error bars where relevant.

    Recall that you can always retrieve the maximum *point* x-value of a TGraph object
    with ``ROOT.TMath.MaxElement(gr.GetN(), gr.GetX())``.

    The value returned depends on the type of TGraph given:

    - TGraph: the graphs's maximum ``point`` value.
    - TGraphErrors: the graph's maximum ``point + error`` value.
    - TGraphAsymmErrors: the graph's maximum ``point + error_high`` value.

    Parameters
    ----------
    graph : ROOT TGraph, TGraphErrors or TGraphAsymmErrors
        The ROOT graph object.

    Returns
    -------
    xmax : scalar
        Maximum x-value of graph.
    """
    if isinstance(graph, root.TGraphAsymmErrors):
        array = np.ndarray(
            shape=graph.GetN(), dtype="f8", buffer=graph.GetX()
        ) + np.ndarray(shape=graph.GetN(), dtype="f8", buffer=graph.GetEXhigh())

    elif isinstance(graph, root.TGraphErrors):
        array = np.ndarray(
            shape=graph.GetN(), dtype="f8", buffer=graph.GetX()
        ) + np.ndarray(shape=graph.GetN(), dtype="f8", buffer=graph.GetEX())

    elif isinstance(graph, root.TGraph):
        array = np.ndarray(shape=graph.GetN(), dtype="f8", buffer=graph.GetX())

    else:
        TypeError(
            f"graph must be an instance of ROOT.TGraph, ROOT.TGraphErrors or "
            f"ROOT.TGraphAsymmErrors, not {type(graph)}"
        )

    return np.amax(array)


def graph_xmin(graph, only_pos=False):
    """Returns the graph's minimum x-value, including error bars where relevant.

    Recall that you can always retrieve the minimum *point* x-value of a TGraph object
    with ``ROOT.TMath.MinElement(gr.GetN(), gr.GetX())``.

    The value returned depends on the type of TGraph given:

    - TGraph: the graphs's minimum ``point`` value.
    - TGraphErrors: the graph's minimum ``point - error`` value.
    - TGraphAsymmErrors: the graph's minimum ``point - error_low`` value.

    Parameters
    ----------
    graph : ROOT TGraph, TGraphErrors or TGraphAsymmErrors
        The ROOT graph object.

    only_pos : bool, optional
        Only include positive values when searching for the minimum. All points are
        included by default.

        This option is useful for setting the x-axis limits when it is in log scale.

    Returns
    -------
    xmin : scalar
        Minimum x-value of graph.
    """
    if isinstance(graph, root.TGraphAsymmErrors):
        array = np.ndarray(
            shape=graph.GetN(), dtype="f8", buffer=graph.GetX()
        ) - np.ndarray(shape=graph.GetN(), dtype="f8", buffer=graph.GetEXlow())

    elif isinstance(graph, root.TGraphErrors):
        array = np.ndarray(
            shape=graph.GetN(), dtype="f8", buffer=graph.GetX()
        ) - np.ndarray(shape=graph.GetN(), dtype="f8", buffer=graph.GetEX())

    elif isinstance(graph, root.TGraph):
        array = np.ndarray(shape=graph.GetN(), dtype="f8", buffer=graph.GetX())

    else:
        TypeError(
            f"graph must be an instance of ROOT.TGraph, ROOT.TGraphErrors or "
            f"ROOT.TGraphAsymmErrors, not {type(graph)}"
        )

    if only_pos:
        array = array[array > 0]

    return np.amin(array)


def multigraph_ymax(multigraph):
    """Interface to `graph_ymax` if the graph is a ROOT TMultiGraph.

    Parameters
    ----------
    multigraph : ROOT TMultiGraph
        The ROOT multi-graph object.

    Returns
    -------
    ymax : scalar
        Maximum y-value of graph.
    """
    if not isinstance(multigraph, root.TMultiGraph):
        raise TypeError(f"graph must be a ROOT.TMultiGraph, not {type(multigraph)}")

    ymaxs = []

    for graph in multigraph:
        ymaxs.append(graph_ymax(graph))

    return np.amax(ymaxs)


def multigraph_ymin(multigraph, only_pos=False):
    """Interface to `graph_ymin` if the graph is a ROOT TMultiGraph.

    Parameters
    ----------
    multigraph : ROOT TMultiGraph
        The ROOT multi-graph object.

    only_pos : bool, optional
        Only include positive values when searching for the minimum. All points are
        included by default. See `graph_ymin`.

    Returns
    -------
    ymin : scalar
        Minimum y-value of graph.
    """
    if not isinstance(multigraph, root.TMultiGraph):
        raise TypeError(f"graph must be a ROOT.TMultiGraph, not {type(multigraph)}")

    ymins = []

    for graph in multigraph:
        ymins.append(graph_ymin(graph, only_pos))

    return np.amin(ymins)


def multigraph_xmax(multigraph):
    """Interface to `graph_xmax` if the graph is a ROOT TMultiGraph.

    Parameters
    ----------
    multigraph : ROOT TMultiGraph
        The ROOT multi-graph object.

    Returns
    -------
    xmax : scalar
        Maximum x-value of graph.
    """
    if not isinstance(multigraph, root.TMultiGraph):
        raise TypeError(f"graph must be a ROOT.TMultiGraph, not {type(multigraph)}")

    xmaxs = []

    for graph in multigraph:
        xmaxs.append(graph_xmax(graph))

    return np.amax(xmaxs)


def multigraph_xmin(multigraph, only_pos=False):
    """Interface to `graph_xmin` if the graph is a ROOT TMultiGraph.

    Parameters
    ----------
    multigraph : ROOT TMultiGraph
        The ROOT multi-graph object.

    only_pos : bool, optional
        Only include positive values when searching for the minimum. All points are
        included by default. See `graph_xmin`.

    Returns
    -------
    xmin : scalar
        Minimum x-value of graph.
    """
    if not isinstance(multigraph, root.TMultiGraph):
        raise TypeError(f"graph must be a ROOT.TMultiGraph, not {type(multigraph)}")

    xmins = []

    for graph in multigraph:
        xmins.append(graph_xmin(graph, only_pos))

    return np.amin(xmins)


def hist_to_graph(hist, bin_err="none", show_bin_width=False, norm=False):
    """Convert histogram (TH1) to graph (TGraph).

    Parameters
    ----------
    hist : ROOT TH1
        The ROOT histogram.

    bin_err : str, TH1.EBinErrorOpt, optional
        Type of bin error to use. Choose from the following options:

        - 'none': use the bin-error option already defined in `hist`. This is
          the default option.
        - 'normal' or `ROOT.TH1.EBinErrorOpt.kNormal`: errors with Normal (Wald)
          approximation: errorUp = errorLow = sqrt(N).
        - 'poisson' or `ROOT.TH1.EBinErrorOpt.kPoisson`: errors from Poisson
          interval at 68.3% (1 sigma).
        - 'poisson2' or `ROOT.TH1.EBinErrorOpt.kPoisson2`: errors from Poisson
          interval at 95% CL (~2 sigma).

        For more details, see `TH1.EBinErrorOpt`_.

        .. _TH1.EBinErrorOpt: \
            https://root.cern.ch/doc/master/classTH1.html#ac6e38c12259ab72c0d574614ee5a61c7

    show_bin_width : bool, optional
        If True, use graph x error bars to show bin width and place marker at centre of
        bin. The x error bars are set to 0 by default.

    norm : bool, optional
        Normalize the resulting graph such that the y value of each point is 1 and the
        error is y_err/y. The x values and their errors remain the same. This is useful
        for showing the relative error of a histogram in a ratio plot, for example.

    Returns
    -------
    ROOT TGraphAsymmErrors:
        TGraph equivalent of `hist`.
    """
    if bin_err != "none":
        # Make copy of histogram since we'll need to modify its bin error option
        tmp_hist = hist.Clone(hist.GetName() + "_tmp")
    else:
        tmp_hist = hist

    # Convert to and return as graph
    graph = root.TGraphAsymmErrors(tmp_hist.GetNbinsX())

    # Recall in ROOT, the first bin has index 1 (bin 0 is underflow)!
    for i_bin in range(1, tmp_hist.GetNbinsX() + 1):
        N = tmp_hist.GetBinContent(i_bin)

        if not norm:
            graph.SetPoint(i_bin - 1, tmp_hist.GetBinCenter(i_bin), N)
        else:
            graph.SetPoint(i_bin - 1, tmp_hist.GetBinCenter(i_bin), 1.0)

        # Get errors
        if bin_err == "none":
            pass
        elif bin_err == "normal" or bin_err == root.TH1.EBinErrorOpt.kNormal:
            tmp_hist.SetBinErrorOption(root.TH1.EBinErrorOpt.kNormal)
        elif bin_err == "poisson" or bin_err == root.TH1.EBinErrorOpt.kPoisson:
            tmp_hist.SetBinErrorOption(root.TH1.EBinErrorOpt.kPoisson)
        elif bin_err == "poisson2" or bin_err == root.TH1.EBinErrorOpt.kPoisson2:
            tmp_hist.SetBinErrorOption(root.TH1.EBinErrorOpt.kPoisson2)
        else:
            raise ValueError(f"unknown bin error option '{bin_err}'")

        if not norm:
            y_err_lo = tmp_hist.GetBinErrorLow(i_bin)
            y_err_up = tmp_hist.GetBinErrorUp(i_bin)
        elif norm and N != 0:
            y_err_lo = tmp_hist.GetBinErrorLow(i_bin) / N
            y_err_up = tmp_hist.GetBinErrorUp(i_bin) / N
        else:
            y_err_lo = tmp_hist.GetBinErrorLow(i_bin)
            y_err_up = tmp_hist.GetBinErrorUp(i_bin)

        if show_bin_width:
            # Use x error bars to show bin width
            x_err_lo = tmp_hist.GetBinWidth(i_bin) / 2
            x_err_up = x_err_lo

        else:
            # No x error bars
            x_err_lo = 0.0
            x_err_up = 0.0

        graph.SetPointError(i_bin - 1, x_err_lo, x_err_up, y_err_lo, y_err_up)

    if bin_err != "none":
        # Delete the clone of `hist`
        del tmp_hist

    return graph


def graph(x, y, xerr=None, yerr=None):
    """Create a ROOT TGraph from array-like input.

    Parameters
    ----------
    x, y : float or array-like, shape (n, )
        The data positions.

    xerr, yerr : float or array-like, shape (n, ), optional
        Error bar sizes in the *x* and *y* directions. The default is `None`, in which
        case no error bars are added in this direction.

    Returns
    -------
    ROOT.TGraph or ROOT.TGraphErrors
        TGraph object created from input arrays.
    """
    # Convert input arrays to flattened, double-precision, contiguous arrays
    x = np.ravel(x).astype(np.float64, order="C", copy=False)
    y = np.ravel(y).astype(np.float64, order="C", copy=False)

    if x.size != y.size:
        raise ValueError("x and y must be the same size")

    # Process x errors
    if xerr is not None:
        if not np.iterable(xerr):
            xerr = np.ones_like(x) * xerr

        xerr = np.ravel(xerr).astype(np.float64, order="C", copy=False)

        if xerr.size != x.size:
            raise ValueError("xerr must be same size as x")

    # Process y errors
    if yerr is not None:
        if not np.iterable(yerr):
            yerr = np.ones_like(y) * yerr

        yerr = np.ravel(yerr).astype(np.float64, order="C", copy=False)

        if yerr.size != y.size:
            raise ValueError("yerr must be same size as y")

    # Create graph object
    if xerr is None and yerr is None:
        graph = root.TGraph(x.size, x, y)

    elif xerr is not None and yerr is None:
        graph = root.TGraphErrors(x.size, x, y, xerr, root.nullptr)

    elif xerr is None and yerr is not None:
        graph = root.TGraphErrors(x.size, x, y, root.nullptr, yerr)

    elif xerr is not None and yerr is not None:
        graph = root.TGraphErrors(x.size, x, y, xerr, yerr)

    return graph


def set_graphics_attributes(obj, **kwargs):
    """Set an object's graphics attributes.

    Parameters
    ----------
    obj : ROOT TObject
        Any ROOT object that inherits from a graphics-attribute class, currently limited
        to TAttLine, TAttFill, TAttMarker and TAttText.
    **kwargs : formatting options, optional
        `kwargs` are used to specify properties like marker, line, and fill attributes.
        See the ROOT docs for available options:

            | https://root.cern.ch/doc/master/classTAttLine.html
            | https://root.cern.ch/doc/master/classTAttFill.html
            | https://root.cern.ch/doc/master/classTAttMarker.html
            | https://root.cern.ch/doc/master/classTAttText.html

        The kwarg syntax is the same as the equivalent ROOT attribute setter function,
        but in all lower case and without the 'Set' prefix. For example, to set the
        marker style, use ``markerstyle=...``, which calls ``SetMarkerStyle(...)``.
    """
    if not isinstance(obj, root.TObject):
        raise TypeError(f"object must be an instance of ROOT::TObject, not {type(obj)}")

    # Line attributes
    if isinstance(obj, root.TAttLine):
        if "linecolor" in kwargs and "linealpha" not in kwargs:
            obj.SetLineColor(get_color_code(kwargs["linecolor"]))

        if "linecolor" in kwargs and "linealpha" in kwargs:
            obj.SetLineColorAlpha(
                get_color_code(kwargs["linecolor"]), kwargs["linealpha"]
            )

        if "linewidth" in kwargs:
            obj.SetLineWidth(kwargs["linewidth"])

        if "linestyle" in kwargs:
            obj.SetLineStyle(kwargs["linestyle"])

    # Fill attributes
    if isinstance(obj, root.TAttFill):
        if "fillcolor" in kwargs and "fillalpha" not in kwargs:
            obj.SetFillColor(get_color_code(kwargs["fillcolor"]))

        if "fillcolor" in kwargs and "fillalpha" in kwargs:
            obj.SetFillColorAlpha(
                get_color_code(kwargs["fillcolor"]), kwargs["fillalpha"]
            )

        if "fillstyle" in kwargs:
            obj.SetFillStyle(kwargs["fillstyle"])

    # Marker attributes
    if isinstance(obj, root.TAttMarker):
        if "markercolor" in kwargs and "markeralpha" not in kwargs:
            obj.SetMarkerColor(get_color_code(kwargs["markercolor"]))

        if "markercolor" in kwargs and "markeralpha" in kwargs:
            obj.SetMarkerColorAlpha(
                get_color_code(kwargs["markercolor"]), kwargs["markeralpha"]
            )

        if "markersize" in kwargs:
            obj.SetMarkerSize(kwargs["markersize"])

        if "markerstyle" in kwargs:
            obj.SetMarkerStyle(kwargs["markerstyle"])

    # Text attributes
    if isinstance(obj, root.TAttText):
        if "textsize" in kwargs:
            obj.SetTextSize(kwargs["textsize"])

        if "textfont" in kwargs:
            obj.SetTextFont(kwargs["textfont"])

        if "textalign" in kwargs:
            obj.SetTextAlign(kwargs["textalign"])

        if "textcolor" in kwargs and "textalpha" not in kwargs:
            obj.SetTextColor(get_color_code(kwargs["textcolor"]))

        if "textcolor" in kwargs and "textalpha" in kwargs:
            obj.SetTextColorAlpha(
                get_color_code(kwargs["textcolor"]), kwargs["textalpha"]
            )

        if "textangle" in kwargs:
            obj.SetTextAngle(kwargs["textangle"])


def set_axis_attributes(obj, **kwargs):
    """Set a TAxis object's attributes.

    Parameters
    ----------
    obj : ROOT TAxis
        A ROOT TAxis object, e.g. from ``TH1::GetXaxis()``.
    **kwargs : formatting options, optional
        `kwargs` are used to specify the axis attributes. See the ROOT docs for
        available options:

            | https://root.cern.ch/doc/master/classTAttAxis.html

        The kwarg syntax is the same as the equivalent ROOT attribute setter function,
        but in all lower case and without the 'Set' prefix. For example, to set the
        axis title size, use ``titlesize=...``, which calls ``SetTitleSize(...)``.
    """
    # Axis attributes
    if not isinstance(obj, root.TAttAxis):
        warnings.warn(
            "set_axis_attributes: object is not a TAttAxis object", stacklevel=2
        )
        return

    if "ndivisions" in kwargs:
        if isinstance(kwargs["ndivisions"], int):
            obj.SetNdivisions(kwargs["ndivisions"])
        elif len(kwargs["ndivisions"]) == 3 and all(
            isinstance(x, int) for x in kwargs["ndivisions"]
        ):
            obj.SetNdivisions(*kwargs["ndivisions"])
        else:
            warnings.warn(
                f"set_axis_attributes: ignoring invalid ndivisions argument '{kwargs['ndivisions']}'"
            )

    if "axiscolor" in kwargs:
        obj.SetAxisColor(get_color_code(kwargs["axiscolor"]))

    if "axiscolor" in kwargs and "axisalpha" in kwargs:
        obj.SetAxisColor(get_color_code(kwargs["axiscolor"]), kwargs["axisalpha"])

    if "labelcolor" in kwargs:
        obj.SetLabelColor(get_color_code(kwargs["labelcolor"]))

    if "labelcolor" in kwargs and "labelalpha" in kwargs:
        obj.SetAxisColor(get_color_code(kwargs["labelcolor"]), kwargs["labelalpha"])

    if "labelfont" in kwargs:
        obj.SetLabelFont(kwargs["labelfont"])

    if "labeloffset" in kwargs:
        obj.SetLabelOffset(kwargs["labeloffset"])

    if "labelsize" in kwargs:
        obj.SetLabelSize(kwargs["labelsize"])

    if "ticklength" in kwargs:
        obj.SetTickLength(kwargs["ticklength"])

    if "ticksize" in kwargs:
        obj.SetTickSize(kwargs["ticksize"])

    if "titleoffset" in kwargs:
        obj.SetTitleOffset(kwargs["titleoffset"])

    if "titlesize" in kwargs:
        obj.SetTitleSize(kwargs["titlesize"])

    if "titlecolor" in kwargs:
        obj.SetTitleColor(get_color_code(kwargs["titlecolor"]))

    if "titlefont" in kwargs:
        obj.SetTitleFont(kwargs["titlefont"])


def get_color_code(color):
    """Get ROOT colour code from arbitrary input.

    Parameters
    ----------
    color : str, tuple, int
        The input colour. Must be one of:
          - Name of ROOT's predefined colours (str): white, black, gray, red, green,
            blue, yellow, magenta, cyan, orange, spring, teal, azure, violet, pink.
          - Colour hex code (str beginning with '#').
          - RGB (red, green, blue) tuple of integers in the range [0, 255] or floats in
            the range [0, 1].
          - ROOT colour code (int). If this is the case, `colour` is returned as is.
    """
    if isinstance(color, int):
        # Already a ROOT colour code
        return color

    elif isinstance(color, str) and color[0] != "#":
        # Predefined colour
        c = color.lower()

        if c in {"w", "white"}:
            return root.kWhite
        elif c in {"k", "black"}:
            return root.kBlack
        elif c in {"gray", "grey"}:
            return root.kGray
        elif c in {"r", "red"}:
            return root.kRed
        elif c in {"g", "green"}:
            return root.kGreen
        elif c in {"b", "blue"}:
            return root.kBlue
        elif c in {"y", "yellow"}:
            return root.kYellow
        elif c in {"m", "magenta"}:
            return root.kMagenta
        elif c in {"c", "cyan"}:
            return root.kCyan
        elif c in {"o", "orange"}:
            return root.kOrange
        elif c in {"s", "spring"}:
            return root.kSpring
        elif c in {"t", "teal"}:
            return root.kTeal
        elif c in {"a", "azure"}:
            return root.kAzure
        elif c in {"v", "violet"}:
            return root.kViolet
        elif c in {"p", "pink"}:
            return root.kPink
        else:
            raise ValueError(f"unknown colour {color}")

    elif isinstance(color, str) and color[0] == "#":
        # Hex code
        return root.TColor.GetColor(color)

    elif isinstance(color, tuple) and len(color) == 3:
        # RGB tuple
        if all(isinstance(x, int) for x in color) or all(
            isinstance(x, float) for x in color
        ):
            return root.TColor.GetColor(*color)

    else:
        raise TypeError(f"invalid color '{color}'")
