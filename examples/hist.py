#!/usr/bin/env python3
"""
Example: Random Histogram
=========================

This module plots a random histogram using the ATLAS Style.
"""

import ROOT as root
import atlasplots as aplt

root.gROOT.SetBatch()


def main():
    # Set the ATLAS Style
    aplt.set_atlas_style()

    # Create a figure and axes
    fig, ax = aplt.subplots(1, 1, name="fig1", figsize=(800, 600))

    # Define a distribution
    sqroot = root.TF1("sqroot", "x*gaus(0) + [3]*abs(sin(x)/x)", 0, 10)
    sqroot.SetParameters(10, 4, 1, 20)

    # Randomly fill the histogram according to the above distribution
    hist = root.TH1F("hist", "Random Histogram", 50, 0, 10)
    hist.FillRandom("sqroot", 20000)

    # Fit the histogram with the original distribution; store graphics func but do not draw
    hist.Fit("sqroot", "0")

    # Draw the histogram on these axes
    ax.plot(hist, label="Random Hist", labelfmt="F")

    # Draw the fit function
    sqroot.SetNpx(1000)
    ax.plot(sqroot, label="Fit", labelfmt="L", linecolor=root.kRed+1)

    # Add extra space at top of plot to make room for labels
    ax.add_margins(top=0.16)

    # Set axis titles
    ax.set_xlabel("X [GeV]")
    ax.set_ylabel("Events / 0.2 GeV")

    # Add the ATLAS Label
    aplt.atlas_label(text="Internal", loc="upper left")
    ax.text(0.2, 0.86, "#sqrt{s} = 13 TeV, 139 fb^{-1}", size=22, align=13)

    # Add legend
    ax.legend(loc=(0.65, 0.8, 0.95, 0.92))

    # Save the plot as a PDF
    fig.savefig("hist.pdf")


if __name__ == '__main__':
    main()
