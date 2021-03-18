#!/usr/bin/env python3
"""
Ratio Plot
==========

This example plots two random histograms and their ratios using the ATLAS Style.

.. literalinclude:: ../examples/ratio.py
    :lines: 12-
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

    # Randomly fill two histograms according to the above distribution
    hist1 = root.TH1F("hist1", "Random Histogram 1", 50, 0, 10)
    hist1.FillRandom("sqroot", 20000)

    sqroot.SetParameters(10, 4, 1.1, 20)
    hist2 = root.TH1F("hist2", "Random Histogram 2", 50, 0, 10)
    hist2.FillRandom("sqroot", 20000)

    # Draw the histograms on these axes
    ax1.plot(hist1, linecolor=root.kRed+1, label="Red", labelfmt="L")
    ax1.plot(hist2, linecolor=root.kBlue+1, label="Blue", labelfmt="L")

    # Draw line at y=1 in ratio panel
    line = root.TLine(ax1.get_xlim()[0], 1, ax1.get_xlim()[1], 1)
    ax2.plot(line)

    # Calculate and draw the ratio
    ratio_hist = hist1.Clone("ratio_hist")
    ratio_hist.Divide(hist2)
    ax2.plot(ratio_hist, linecolor=root.kBlack)

    # Add extra space at top of plot to make room for labels
    ax1.add_margins(top=0.16)

    # Set axis titles
    ax2.set_xlabel("X [GeV]")
    ax1.set_ylabel("Events / 0.2 GeV")
    ax2.set_ylabel("Red / Blue", loc="centre")

    # Add extra space at top and bottom of ratio panel
    ax2.add_margins(top=0.1, bottom=0.1)

    # Go back to top axes to add labels
    ax1.cd()

    # Add the ATLAS Label
    aplt.atlas_label(text="Internal", loc="upper left")
    ax1.text(0.2, 0.84, "#sqrt{s} = 13 TeV, 139 fb^{-1}", size=22, align=13)

    # Add legend
    ax1.legend(loc=(0.78, 0.78, 1, 0.90))

    # Save the plot as a PDF
    fig.savefig("ratio.pdf")


if __name__ == '__main__':
    root.gROOT.SetBatch()
    main()
