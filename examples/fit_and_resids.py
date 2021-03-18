#!/usr/bin/env python3
"""
Fit Histogram and Show Residuals
================================

This example generates and plots a random histogram, fits the original function
to the generated distribution, and displays the fit residuals in the lower panel.

.. literalinclude:: ../examples/fit_and_resids.py
    :lines: 13-
"""

import ROOT as root
import atlasplots as aplt


def main():
    # Set the ATLAS Style
    aplt.set_atlas_style()

    # Create a figure and axes
    fig, (ax1, ax2) = aplt.ratio_plot(name="fig1", figsize=(800, 800), hspace=0.05)

    # Define a distribution
    sqroot = root.TF1("sqroot", "x*gaus(0) + [3]*abs(sin(x)/x)", 0, 10)
    sqroot.SetParameters(10, 4, 1, 20)

    # Randomly fill the histogram according to the above distribution
    hist = root.TH1F("hist", "Random Histogram", 50, 0, 10)
    hist.FillRandom("sqroot", 20000)

    # Fit the histogram with the original distribution; store graphics func but do not draw
    hist.Fit("sqroot", "0")

    # Draw the histogram on these axes
    ax1.plot(hist, "EP", linewidth=1, label="Random Hist", labelfmt="EP")

    # Draw the fit function
    sqroot.SetNpx(1000)
    ax1.plot(sqroot, linecolor=root.kRed+1, label="Fit", labelfmt="L")

    # Draw line at y=0 in residuals panel
    line = root.TLine(ax1.get_xlim()[0], 0, ax1.get_xlim()[1], 0)
    ax2.plot(line)

    # Calculate and draw the fit residuals
    resids = hist.Clone("resids")
    for i in range(1, resids.GetNbinsX()):
        resids.SetBinContent(i, hist.GetBinContent(i) - sqroot.Eval(hist.GetBinCenter(i)))
        resids.SetBinError(i, hist.GetBinError(i))

    ax2.plot(resids, "EP", linewidth=1)

    # Add extra space at top of plot to make room for labels
    ax1.add_margins(top=0.16)

    # Add extra space at top and bottom of residuals panel
    ax2.add_margins(top=0.1, bottom=0.1)

    # Set axis titles
    ax2.set_xlabel("X [GeV]")
    ax1.set_ylabel("Events / 0.2 GeV")
    ax2.set_ylabel("Data - Fit", loc="center")

    # Go back to top axes to add labels
    ax1.cd()

    # Add the ATLAS Label
    aplt.atlas_label(text="Internal", loc="upper left")
    ax1.text(0.2, 0.84, "#sqrt{s} = 13 TeV, 139 fb^{-1}", size=22, align=13)

    # Add legend
    ax1.legend(loc=(0.65, 0.78, 0.92, 0.90))

    # Save the plot as a PDF
    fig.savefig("fit_and_resids.pdf")


if __name__ == '__main__':
    root.gROOT.SetBatch()
    main()
