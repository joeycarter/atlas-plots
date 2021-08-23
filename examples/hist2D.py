#!/usr/bin/env python3
"""
Random 2D Histogram
===================

This example plots a random, 2D histogram using the ATLAS Style.

.. literalinclude:: ../examples/hist2D.py
    :lines: 12-
"""

import ROOT as root
import atlasplots as aplt


root.gInterpreter.Declare("""
void fillHist2D(TH2F* hist, int N) {
    float px, py;
    for (Int_t i = 0; i < N; i++) {
        gRandom->Rannor(px, py);
        hist->Fill(px + 4, 25 * py + 100);
        hist->Fill(0.5 * px + 8, 12 * py + 50, 0.1);
    }
}
""")


def main():
    # Set the ATLAS Style
    aplt.set_atlas_style()

    # Create a figure and axes
    fig, ax = aplt.subplots(1, 1, name="fig1", figsize=(800, 600))

    # Randomly fill a 2D histogram
    hist = root.TH2F("hist", "Random Histogram", 50, 0, 10, 40, 0, 200)
    root.fillHist2D(hist, 50000)

    # Draw the histogram on these axes
    ax.plot2d(hist, "COLZ")

    # Change pad margins to allow space for z-axis colour bar and for ATLAS label
    ax.pad.SetRightMargin(0.18)
    ax.pad.SetTopMargin(0.08)

    # Set axis titles
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Events / (0.2 #times 5)")

    # Add the ATLAS Label
    aplt.atlas_label(ax.pad.GetLeftMargin(), 0.97, text="Internal", align=13)
    ax.text(1 - ax.pad.GetRightMargin(), 0.97, "#sqrt{s} = 13 TeV, 139 fb^{-1}", size=22, align=33)

    # Save the plot as a PDF
    fig.savefig("hist2D.pdf")


if __name__ == '__main__':
    root.gROOT.SetBatch()
    main()
