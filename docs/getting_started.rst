.. _getting_started:

Getting Started
===============

.. contents::
   :local:

Before You Begin
----------------

To use **atlasplots** you will need a working installation of `ROOT <https://root.cern.ch/>`_, a scientific software framework developed at CERN for data analysis in high energy physics.
You can install **ROOT** by following the `Installing ROOT <https://root.cern/install/>`_ guide on their website.
If you are a newcomer to ROOT, there are a number of resources available to help get started.
A good starting point is the `ROOT Primer <https://root.cern/primer/>`_ beginner's guide.
`Courses <https://root.cern/get_started/courses/>`_ and `Tutorials <https://root.cern/tutorials/>`_ are also available.

PyROOT
^^^^^^

**atlasplots** uses `PyROOT <https://root.cern/manual/python/>`_, ROOT's Python-C++ bindings.
With **PyROOT** you can access the full ROOT functionality from Python while benefiting from the performance of the ROOT C++ libraries.

When ROOT is installed, you can use PyROOT both from the Python prompt and from a Python script.
The entry point to PyROOT is the ``ROOT`` module, which you must import first:

>>> import ROOT

Then you can access the ROOT C++ classes, functions, etc. via the ``ROOT`` module.


Installing atlasplots
---------------------

**atlasplots** is not in PyPI (yet) so for now it's best to install as editable:

.. code-block:: console

    $ pip install -e https://github.com/joeycarter/atlas-plots

Replace ``https://github.com/joeycarter/atlas-plots`` with ``git@github.com:joeycarter/atlas-plots.git`` if you have GitHub ``ssh`` keys set up.

To uninstall:

.. code-block:: console

    $ pip uninstall atlasplots


Installing on lxplus
^^^^^^^^^^^^^^^^^^^^

.. note::

    Fellow ATLAS members: follow these instructions to set up **atlasplots** on ``lxplus``.
    Other CERN folk, you may have to fill in some of the gaps to set up your preferred versions of ROOT and Python.

If you want to use **atlasplots** on ``lxplus`` (to avoid copying over potentially large ROOT files to your local machine), there are a few extra steps involved to install it.
As of writing these docs, the default versions of ROOT and Python installed on ``lxplus`` should be sufficient to install **atlasplots**.
However, if you wish to use a more complete, stable release of ROOT, Python, and a number of useful Python packages, you can use an `LCG Release <http://lcginfo.cern.ch/>`_, such as `LCG_98python3 <http://lcginfo.cern.ch/release/98python3/>`_.
To set up the environemtn on ``lxplus``, run:

.. code-block:: bash

    $ setupATLAS
    $ lsetup "views LCG_98python3 x86_64-centos7-gcc9-opt"

You can replace ``LCG_98python3`` and ``x86_64-centos7-gcc9-opt`` with your preferred LCG release and OS/compiler architecture.

.. warning::

    Careful here: setting up ROOT in this way might interfere with certain environment and ``PATH`` variables if you have an ``Athena`` release set up in your current shell.

The LCG release should come with ``pip`` out of the box.
In general, to install a package on ``lxplus``, use the ``--user`` flag in your ``pip`` command:

.. code-block:: console

    $ pip install --user <package>

This tells ``pip`` to install packages to ``~/.local/lib/`` (which is necessary since you don't have ``sudo`` privileges on ``lxplus``).
Finally, install **atlasplots** with:

.. code-block:: console

    $ pip install --user -e https://github.com/joeycarter/atlas-plots


Basic Usage
-----------

**Behold, the simplicity of atlasplots:**

.. code-block:: python

    import atlasplots as aplt

    aplt.set_atlas_style()

    fig, ax = aplt.subplots(1, 1)
    ax.set_xlabel("X [GeV]")
    ax.set_ylabel("Events")
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 10)

    fig.savefig("figure.png")

.. image:: _static/figure.png
    :align: center
    :alt: figure.png

For a collection of complete examples, see the :ref:`examples` section.
