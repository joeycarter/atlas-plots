#!/usr/bin/env python3
"""
Graph from Numpy Array
======================

This example plots a graph directly from numpy arrays using the ATLAS Style.

.. literalinclude:: ../examples/numpy_graph.py
    :lines: 12-
"""

import numpy as np

import ROOT as root
import atlasplots as aplt


def main():
    # Set the ATLAS Style
    aplt.set_atlas_style()

    # Create a figure and axes
    fig, ax = aplt.subplots(1, 1, name="fig1", figsize=(800, 600))

    # Plot a line with Gaussian noise
    x = np.arange(20)
    y = 2 * x + np.random.normal(size=20)
    yerr = np.random.normal(loc=np.linspace(1, 2, num=20), scale=0.1, size=20)

    graph = ax.graph(x, y, yerr=yerr, label="Data", labelfmt="EP")

    # Fit the graph; store graphics func but do not draw
    graph.Fit("pol1", "0")

    # Add extra space at top of plot to make room for labels
    ax.add_margins(top=0.18, left=0.05, right=0.05, bottom=0.05)

    # Plot fit function and extend its range to fill plot area
    func = graph.GetFunction("pol1")
    func.SetRange(*ax.get_xlim())
    func.SetNpx(1000)
    ax.plot(func, linecolor=root.kRed+1, expand=False, label="Fit", labelfmt="L")

    # Set axis titles
    ax.set_xlabel("x")
    ax.set_ylabel("y")

    # Add the ATLAS Label
    aplt.atlas_label(text="Simulation Internal", loc="upper left")

    # Add legend
    ax.legend(loc=(0.65, 0.8, 0.95, 0.92))

    # Save the plot as a PDF
    fig.savefig("numpy_graph.pdf")


if __name__ == '__main__':
    root.gROOT.SetBatch()
    main()
