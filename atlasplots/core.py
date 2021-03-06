"""
atlasplots.core
~~~~~~~~~~~~~~~

This module contains the primary objects and methods that power ATLAS Plots.

:copyright: (c) 2020 Joey Carter.
:license: MIT, see LICENSE for more details.
"""

import random
import string
import warnings

import numpy as np

import ROOT as root

from . import root_helpers


__all__ = [
    "Figure",
    "Axes",
]


def _rand_str(size=16):
    """Return a random string of lowercase ascii character.

    ROOT requires some objects, like TH1s and TPads, to have unique names; using
    random strings is one way to ensure there are no clashing names if you do
    not want to explicitly name these objects.

    Parameters
    ----------
    size : int, optional
        Length of random string. The default is 16.

    Returns
    -------
    out : str
        Random string of lowercase ascii character of length `size`.
    """
    return "".join(random.SystemRandom().choices(string.ascii_lowercase, k=size))


class Figure:
    """A matplotlib-like `Figure` object powered by ROOT.

    A `Figure` object is a wrapper around a ROOT TCanvas. `Figure` provides
    matplotlib-like syntax to change figure parameters while still providing
    access to the underlying ROOT objects.
    """

    def __init__(self, name="", title="", figsize=None):
        """
        Parameters
        ----------
        name : str, optional
            Figure (canvas) name.

        title : str, optional
            Figure (canvas) title.

        figsize : (float, float), optional
            Figure (canvas) dimension `(width, height)` in pixels. The default
            dimensions are (800, 600).
        """
        if figsize is None:
            figsize = (800, 600)
        elif not np.isfinite(figsize).all() or (np.array(figsize) < 0).any():
            raise ValueError(
                "figure size must be positive finite not {}".format(figsize)
            )

        self._canvas = root.TCanvas(name, title, figsize[0], figsize[1])
        self._axes = np.array([Axes()])

        self._canvas.Update()

    @property
    def canvas(self):
        """Returns the figure's TCanvas object.
        """
        return self._canvas

    @property
    def axes(self):
        """Returns the figure's axes.
        """
        return self._axes

    def subplots(
        self,
        nrows=1,
        ncols=1,
        width_ratios=None,
        height_ratios=None,
        wspace=None,
        hspace=None,
    ):
        """Add a set of subplots to this figure.

        Parameters
        ----------
        nrows, ncols : int, default: 1
            Number of rows/columns of the subplot grid.

        width_ratios : array-like of length `ncols`, optional
            Defines the relative widths of the columns. Each column gets a
            relative width of ``width_ratios[i] / sum(width_ratios)``. If not
            given, all columns will have the same width.

        height_ratios : array-like of length `nrows`, optional
            Defines the relative heights of the rows. Each row gets a relative
            height of ``height_ratios[i] / sum(height_ratios)``. If not given,
            all rows will have the same height.

        wspace : float, optional
            The amount of width reserved for space between subplots, expressed
            as a fraction of the average axis width.
            Not implemented yet...

        hspace : float, optional
            The amount of height reserved for space between subplots, expressed
            as a fraction of the average axis height.
            Not implemented yet...

        Returns
        -------
        axs : `Axes` or array of Axes.
            Either a single `Axes` object or an array of Axes objects if more
            than one subplot was created.
        """
        if width_ratios is not None and len(width_ratios) != ncols:
            raise ValueError(
                "Expected the given number of width ratios to match the "
                "number of columns of the grid"
            )
        if height_ratios is not None and len(height_ratios) != nrows:
            raise ValueError(
                "Expected the given number of height ratios to match the "
                "number of rows of the grid"
            )

        if wspace is not None:
            warnings.warn("The 'wspace' option is not implemented", stacklevel=2)
        if hspace is not None:
            warnings.warn("The 'hspace' option is not implemented", stacklevel=2)

        if width_ratios is None:
            width_ratios = [1] * ncols

        if height_ratios is None:
            height_ratios = [1] * nrows

        # x and y pad limits, starting at 0 and ending at 1
        # Reverse `height_ratios` to make row ordering correct (top to bottom)
        xpos = np.cumsum(([0] + width_ratios) / np.sum(width_ratios))
        ypos = np.cumsum(([0] + height_ratios[::-1]) / np.sum(height_ratios))

        # ROOT requires TH1s and TPads to have unique names; use random string
        rand_str = _rand_str()

        # Create empty array to store Axes objects in grid
        axs = np.ndarray((nrows, ncols), dtype=object)

        for row in range(nrows):
            for col in range(ncols):
                # Construct input arguments to TPad constructor
                pad_args = (
                    "PAD_{}_{}_{}".format(rand_str, row, col),  # name
                    "",  # title
                    xpos[col],  # xlow
                    ypos[-row - 2],  # ylow
                    xpos[col + 1],  # xup
                    ypos[-row - 1],  # yup
                )
                axs[row, col] = Axes(pad_args)
                self._canvas.cd()  # Go back to main canvas

        self._axes = axs

        # If grid has only one column or one row, flatten the returned array
        if ncols == 1 and nrows != 1:
            axs = np.reshape(axs, (1, nrows))[0]
        elif ncols != 1 and nrows == 1:
            axs = np.reshape(axs, (1, ncols))[0]
        elif ncols == 1 and nrows == 1:
            axs = axs[0, 0]

        return axs

    def savefig(self, fname, options=""):
        """Save the figure using ``TCanvas::SaveAs()``.

        Parameters
        ----------
        fname : str or path-like
            File name.
        options : str, optional
            Addition options to pass to ``TCanvas::SaveAs()``.
        """
        self._canvas.SaveAs(fname, options)


class Axes:
    """A matplotlib-like `Axes` object powered by ROOT.

    An `Axes` object is a wrapper around a ROOT TPad and a "frame" (which is an
    empty TH1F histogram object). `Axes` provides matplotlib-like syntax to
    change axis parameters, like ``set_xlim()``, while still providing access to
    the underlying ROOT objects.
    """

    def __init__(self, pad_args=None, frame_args=None):
        """
        Parameters
        ----------
        pad_args : tuple, optional
            Arguments to pass to the TPad constructor.

        frame_args : tuple, optional
            Arguments to pass to the TH1F constructor to create the frame.
        """
        # ROOT requires TH1s and TPads to have unique names; use random string
        rand_str = _rand_str()

        if pad_args is None:
            self._pad = root.TPad("PAD_{}".format(rand_str), "", 0, 0, 1, 1)
        else:
            self._pad = root.TPad(*pad_args)

        if frame_args is None:
            self._frame = root.TH1F("FRAME_{}".format(rand_str), "", 1, 0, 1)
        else:
            self._frame = root.TH1F(*frame_args)

        # Draw the pad and frame
        self._pad.Draw()
        self._pad.cd()
        self._frame.Draw("AXIS")  # Draw axes of `self._frame` only
        self._frame.SetBinContent(1, 1)

        self._logy = False
        self._logx = False

        # So that the TPad and TH1 objects are not lost
        root.SetOwnership(self._pad, False)
        root.SetOwnership(self._frame, False)

    @property
    def pad(self):
        """Returns the axes' TPad object.
        """
        return self._pad

    @property
    def frame(self):
        """Returns the axes' TH1F frame object.
        """
        return self._frame

    def cd(self):
        """Sets these axes as the current axes.

        Equivalent to `ax.pad.cd()` (i.e. ``TPad::cd()``).

        Note that `Axes.cd()` does *not* need to be called before `Axes.plot()`;
        this is done automatically.
        """
        self._pad.cd()

    def plot(self, obj, options=""):
        """Plot object on these axes.

        Note that `Axes.cd()` does *not* need to be called before `Axes.plot()`;
        this is done automatically.

        Parameters
        ----------
        obj : plottable ROOT object
            The object to plot. This object should be a plottable ROOT object,
            such as a TH1, TGraph, TF1, etc., and it must have a ``Draw()``
            method, otherwise a `TypeError` is raised.

        options : str, optional
            Additional options to pass to ``Draw()``.
        """
        self._pad.cd()

        if isinstance(obj, root.TH1):
            # Histgoram
            obj.Draw("HIST SAME " + options)

            # Expand axes to view
            old_left, old_right = self.get_xlim()
            old_bottom, old_top = self.get_ylim()

            left, right = obj.GetXaxis().GetXmin(), obj.GetXaxis().GetXmax()
            bottom, top = root_helpers.hist_min(obj), root_helpers.hist_max(obj)

            new_left = left if left < old_left else old_left
            new_right = right if right > old_right else old_right
            new_bottom = bottom if bottom < old_bottom else old_bottom
            new_top = top if top > old_top else old_top

            self.set_xlim(new_left, new_right)
            self.set_ylim(new_bottom, new_top)

            self._pad.RedrawAxis()

        elif isinstance(obj, root.THStack):
            # Stacked Histgoram
            obj.Draw("SAME HIST" + options)

            top_hist = obj.GetStack().Last()

            # Expand axes to view
            old_left, old_right = self.get_xlim()
            old_bottom, old_top = self.get_ylim()

            left, right = top_hist.GetXaxis().GetXmin(), top_hist.GetXaxis().GetXmax()
            bottom, top = root_helpers.hist_min(top_hist), root_helpers.hist_max(top_hist)

            new_left = left if left < old_left else old_left
            new_right = right if right > old_right else old_right
            new_bottom = bottom if bottom < old_bottom else old_bottom
            new_top = top if top > old_top else old_top

            self.set_xlim(new_left, new_right)
            self.set_ylim(new_bottom, new_top)

            self._pad.RedrawAxis()

        elif isinstance(obj, root.TGraph):
            # Graph
            obj.Draw(options)

            # Expand axes to view
            old_left, old_right = self.get_xlim()
            old_bottom, old_top = self.get_ylim()

            left, right = root_helpers.graph_xmin(obj), root_helpers.graph_xmax(obj)
            bottom, top = root_helpers.graph_ymin(obj), root_helpers.graph_ymax(obj)

            new_left = left if left < old_left else old_left
            new_right = right if right > old_right else old_right
            new_bottom = bottom if bottom < old_bottom else old_bottom
            new_top = top if top > old_top else old_top

            self.set_xlim(new_left, new_right)
            self.set_ylim(new_bottom, new_top)

            self._pad.RedrawAxis()

        elif isinstance(obj, root.TMultiGraph):
            # Multigraph
            obj.Draw(options)

            # Expand axes to view
            old_left, old_right = self.get_xlim()
            old_bottom, old_top = self.get_ylim()

            left, right = root_helpers.multigraph_xmin(obj), root_helpers.multigraph_xmax(obj)
            bottom, top = root_helpers.multigraph_ymin(obj), root_helpers.multigraph_ymax(obj)

            new_left = left if left < old_left else old_left
            new_right = right if right > old_right else old_right
            new_bottom = bottom if bottom < old_bottom else old_bottom
            new_top = top if top > old_top else old_top

            self.set_xlim(new_left, new_right)
            self.set_ylim(new_bottom, new_top)

            self._pad.RedrawAxis()

        else:
            try:
                obj.Draw("SAME " + options)
            except AttributeError:
                raise TypeError("Attempting to plot an object with no Draw() method")

    def text(
        self,
        x,
        y,
        text,
        size=None,
        font=None,
        align=None,
        color=None,
        alpha=None,
        angle=None,
    ):
        """Draws text on these axes using the ROOT TLatex class.

        Parameters
        ----------
        x, y : float
            The x- and y-coordinates of the text in NDC units [0, 1].

            This x-coordinate is left-aligned and the y-coordinate is top-aligned
            unless the `align` argument is given.

        text : str
            The text to draw. ROOT TLatex syntax is supported.

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

        angle : float, optional
            Text angle in degrees.

        Returns
        -------
        ROOT.TLatex
            The TLatex object for this text.
        """
        self._pad.cd()

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

        label.DrawLatex(x, y, text)

        return label

    def set_xscale(self, value):
        """
        Set the x-axis scale.

        Parameters
        ----------
        value : {"linear", "log"}
            The axis scale type to apply.
        """
        if value in ["linear", "lin"]:
            self._pad.SetLogx(0)
            self._logx = False

        elif value in ["log", "logy"]:
            left, right = self.get_xlim()
            if right <= 0:
                warnings.warn(
                    "Current frame has no positive values, and therefore cannot "
                    "be log-scaled. Try running ax.set_xlim() first."
                )
            elif left <= 0:
                # Arbitrarily set left to 0.1 (or 0.1*right if right <= 0.1)
                # so that the frame can be displayed
                if right <= 0.1:
                    self.set_xlim(left=0.1 * right)
                else:
                    self.set_xlim(left=0.1)

            self._pad.cd()
            self._pad.SetLogx(1)
            self._pad.RedrawAxis()
            self._logx = True

    def set_yscale(self, value):
        """
        Set the y-axis scale.

        Parameters
        ----------
        value : {"linear", "log"}
            The axis scale type to apply.
        """
        if value in ["linear", "lin"]:
            self._pad.SetLogy(0)
            self._logy = False

        elif value in ["log", "logy"]:
            bottom, top = self.get_ylim()
            if top <= 0:
                warnings.warn(
                    "Current frame has no positive values, and therefore cannot "
                    "be log-scaled. Try running ax.set_ylim() first."
                )
            elif bottom <= 0:
                # Arbitrarily set bottom to 0.1 (or 0.1*top if top < 0.1)
                # so that the frame can be displayed
                if top <= 0.1:
                    self.set_ylim(bottom=0.1 * top)
                else:
                    self.set_ylim(bottom=0.1)

            self._pad.cd()
            self._pad.SetLogy(1)
            self._pad.RedrawAxis()
            self._logy = True

    def add_margins(self, left=0.0, right=0.0, bottom=0.0, top=0.0):
        """Adds margins between the axes and the data within.

        Parameters
        ----------
        left, right, bottom, top : float, optional
            Margin sizes in NDC units [0, 1]. The default is 0.

        Notes
        -----
        This function sets the margin size with respect to the current x- and
        y-axis limits, therefore multiple calls to ``add_margins()`` will
        incrementally add to the margin size. In most cases, ``add_margins()``
        should only be called once per axes.

        FIXME
        -----
        This function will need to be modified to handle axes in log scale.
        """
        # Check inputs
        if left + right == 1:
            raise ValueError(
                "Attempting to add infinite margins; the sum of left and right "
                "cannot equal 1"
            )
        if bottom + top == 1:
            raise ValueError(
                "Attempting to add infinite margins; the sum of bottom and top "
                "cannot equal 1"
            )

        old_left, old_right = self.get_xlim()
        old_bottom, old_top = self.get_ylim()

        if not self._logy:
            ymin = ((1 - top) * old_bottom - bottom * old_top) / (1 - top - bottom)
            ymax = ((1 - bottom) * old_top - top * old_bottom) / (1 - top - bottom)

        else:
            ymin = np.power(
                10,
                ((1 - top) * np.log10(old_bottom) - bottom * np.log10(old_top)) / (1 - top - bottom)
            )
            ymax = np.power(
                10,
                ((1 - bottom) * np.log10(old_top) - top * np.log10(old_bottom)) / (1 - top - bottom)
            )

        if not self._logx:
            xmin = ((1 - right) * old_left - left * old_right) / (1 - right - left)
            xmax = ((1 - left) * old_right - right * old_left) / (1 - right - left)

        else:
            xmin = np.power(
                10,
                ((1 - right) * np.log10(old_left) - left * np.log10(old_right)) / (1 - right - left)
            )
            xmax = np.power(
                10,
                ((1 - left) * np.log10(old_right) - right * np.log10(old_left)) / (1 - right - left)
            )

        self.set_xlim(xmin, xmax)
        self.set_ylim(ymin, ymax)

    def get_xlabel(self):
        """Get the xlabel text string.
        """
        return self._frame.GetXaxis().GetTitle()

    def set_xlabel(self, xlabel, loc=None):
        """Set the label for the x-axis.

        Parameters
        ----------
        xlabel : str
            The label text.
        loc : {'center', 'right'}
            The label position. The default is the same as ROOT's default x-axis
            title position (right).
        """
        self._frame.GetXaxis().SetTitle(xlabel)

        if loc in ["center", "centre"]:
            self._frame.GetXaxis().CenterTitle()
        elif loc is not None and loc != "right":
            raise ValueError(
                "'{}' is not a valid value for 'loc'; "
                "supported values are {{'center', 'right'}}".format(loc)
            )

        self._pad.Modified()  # Draw the updated axes

    def get_ylabel(self):
        """Get the ylabel text string.
        """
        return self._frame.GetYaxis().GetTitle()

    def set_ylabel(self, ylabel, loc=None):
        """Set the label for the y-axis.

        Parameters
        ----------
        ylabel : str
            The label text.
        loc : {'center', 'top'}
            The label position. The default is the same as ROOT's default y-axis
            title position (top).
        """
        self._frame.GetYaxis().SetTitle(ylabel)

        if loc in ["center", "centre"]:
            self._frame.GetYaxis().CenterTitle()
        elif loc is not None and loc != "top":
            raise ValueError(
                "'{}' is not a valid value for 'loc'; "
                "supported values are {{'center', 'top'}}".format(loc)
            )

        self._pad.Modified()  # Draw the updated axes

    def get_xlim(self):
        """Returns the frame's x-axis limits.

        Returns
        -------
        left, right : (float, float)
            The current x-axis limits in data coordinates.
        """
        return (self._frame.GetXaxis().GetXmin(), self._frame.GetXaxis().GetXmax())

    def get_ylim(self):
        """Returns the frame's y-axis limits.

        Returns
        -------
        bottom, top : (float, float)
            The current y-axis limits in data coordinates.
        """
        return (self._frame.GetMinimum(), self._frame.GetMaximum())

    def set_xlim(self, left=None, right=None):
        """Sets the frame's x-axis limits.

        Parameters
        ----------
        left : float, optional
            The left xlim in data coordinates. Passing `None` leaves the limit
            unchanged.

            The left and right xlims may also be passed as the tuple (`left`,
            `right`) as the first positional argument (or as the `left` keyword
            argument).

        right : float, optional
            The right xlim in data coordinates. Passing `None` leaves the limit
            unchanged.

        Returns
        -------
        left, right : (float, float)
            The new x-axis limits in data coordinates.

        Examples
        --------
        >>> set_xlim(left, right)
        >>> set_xlim((left, right))
        >>> left, right = set_xlim(left, right)

        One limit may be left unchanged.

        >>> set_xlim(right=right_lim)

        Returns
        -------
        left, right : (float, float)
            The new x-axis limits in data coordinates.
        """
        if right is None and np.iterable(left):
            left, right = left

        if left is None or right is None:
            old_left, old_right = self.get_xlim()
            if left is None:
                left = old_left
            if right is None:
                right = old_right

        if left == right:
            warnings.warn(
                "Attempting to set identical left == right == {} x-axis limits".format(
                    left
                ),
                stacklevel=2,
            )

        if left > right:
            raise ValueError("Axis limits must be in increasing order")

        self._frame.GetXaxis().SetLimits(left, right)

        self._pad.Modified()  # Draw the updated axes

        return (left, right)

    def set_ylim(self, bottom=None, top=None):
        """Sets the frame's y-axis limits.

        Parameters
        ----------
        bottom : scalar, optional
            The bottom ylim in data coordinates. Passing `None` leaves the limit
            unchanged.

            The bottom and top ylims may be passed as the tuple (`bottom`,
            `top`) as the first positional argument (or as the `bottom `keyword
            argument).

        top : scalar, optional
            The top ylim in data coordinates. Passing `None` leaves the limit
            unchanged.

        Examples
        --------
        >>> set_ylim(bottom, top)
        >>> set_ylim((bottom, top))
        >>> bottom, top = set_ylim(bottom, top)

        One limit may be left unchanged.

        >>> set_ylim(top=top_lim)

        Returns
        -------
        bottom, top : (float, float)
            The new y-axis limits in data coordinates.
        """
        if top is None and np.iterable(bottom):
            bottom, top = bottom

        if bottom is None or top is None:
            old_bottom, old_top = self.get_ylim()
            if bottom is None:
                bottom = old_bottom
            if top is None:
                top = old_top

        if bottom == top:
            warnings.warn(
                "Attempting to set identical bottom == top == {} y-axis limits".format(
                    bottom
                ),
                stacklevel=2,
            )

        if bottom > top:
            raise ValueError("Axis limits must be in increasing order")

        self._frame.SetMinimum(bottom)
        self._frame.SetMaximum(top)

        self._pad.Modified()  # Draw the updated axes

        return (bottom, top)

    def legend(self, entries, loc=None):
        raise NotImplementedError("Axes.legend() is not implemented yet")
