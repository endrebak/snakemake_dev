.. snakefiles-modularization:

==============
Modularization
==============

Snakemake provides several means for modularization of your workflows.
These features allow you to:

- distribute large workflows over multiple smaller files,
- split workflows into different steps/sub workflows that
    - make things more clear by introducing structure and
    - allow for reuseable sub workflows, and
- use reuseable wrapper scripts for certain tools instead of copy-and-paste code.


.. _snakefiles-includes:

--------
Includes
--------

Another Snakefile with all its rules can be included into the current:

.. code-block:: python

    include: "path/to/other/snakefile"

The default target rule (often called the ``all``-rule), won't be affected by the include.
I.e. it will always be the first rule in your Snakefile, no matter how many includes you have above your first rule.
From version 3.2 on, includes are relative to the directory of the Snakefile in which they occur.
For example, if above Snakefile resides in the directory ``my/dir``, then Snakemake will search for the include at ``my/dir/path/to/other/snakefile``, regardless of the working directory.


.. _snakefiles-sub_workflows:

-------------
Sub-Workflows
-------------

In addition to including rules of another workflow, Snakemake allows to depend on the output of other workflows as sub-workflows.
A sub-workflow is executed independently before the current workflow is executed.
Thereby, Snakemake ensures that all files the current workflow depends on are created or updated if necessary.
This allows to build nice hierarchies of separated workflows and even to separate the directories on disk.

.. code-block:: python

    subworkflow otherworkflow:
        workdir: "../path/to/otherworkflow"
        snakefile: "../path/to/otherworkflow/Snakefile"

    rule a:
        input:  otherworkflow("test.txt")
        output: ...
        shell:  ...

Here, the subworkflow is named "otherworkflow" and it is located in the working directory ``../path/to/otherworkflow``.
The snakefile is in the same directory and called ``Snakefile``.
If ``snakefile`` is not defined for the subworkflow, it is assumed be located in the workdir location and called ``Snakefile``, hence, above we could have left the ``snakefile`` keyword out as well.
If ``workdir`` is not specified, it is assumed to be the same as the current one.
Files that are output from the subworkflow that we depend on are marked with the ``otherworkflow`` function (see the input of rule a).
This function automatically determines the absolute path to the file (here ``../path/to/otherworkflow/test.txt``).

When executing, snakemake first tries to create (or update, if necessary) ``test.txt`` (and all other possibly mentioned dependencies) by executing the subworkflow.
Then the current workflow is executed.
This can also happen recursively, since the subworkflow may have its own subworkflows as well.


.. _snakefiles-wrappers:

--------
Wrappers
--------

With Snakemake 3.5.5, the wrapper directive is introduced (experimental).
This directive allows to have re-usable wrapper scripts around e.g. command line tools. In contrast to modularization strategies like ``include`` or subworkflows, the wrapper directive allows to re-wire the DAG of jobs.
For example

.. code-block:: python

    rule samtools_sort:
        input:
            "mapped/{sample}.bam"
        output:
            "mapped/{sample}.sorted.bam"
        params:
            "-m 4G"
        threads: 8
        wrapper:
            "0.0.8/bio/samtools_sort"

Refers to the wrapper ``"0.0.8/bio/samtools_sort"`` to create the output from the input.
Snakemake will automatically download the wrapper from the `Snakemake Wrapper Repository <https://bitbucket.org/snakemake/snakemake-wrappers>`_.
Thereby, 0.0.8 can be replaced with the git version tag you want to use, or a commit id (see `here <https://bitbucket.org/snakemake/snakemake-wrappers/commits>`_).
This ensures reproducibility since changes in the wrapper implementation won't be propagated automatically to your workflow.
Alternatively, e.g., for development, the wrapper directive can also point to full URLs, including URLs to local files with ``file://``.
Examples for each wrapper can be found in the READMEs located in the wrapper subdirectories at the `Snakemake Wrapper Repository <https://bitbucket.org/snakemake/snakemake-wrappers>`_.

The `Snakemake Wrapper Repository <https://bitbucket.org/snakemake/snakemake-wrappers>`_ is meant as a collaborative project and pull requests are very welcome.


.. _modularization-integrated_package_management:

-----------------------------
Integrated Package Management
-----------------------------

With Snakemake 3.9.0 it is possible to define isolated software environments per rule.
Upon execution of a workflow, the `Conda package manager <http://conda.pydata.org>`_ is used to obtain and deploy the defined software packages in the specified versions. Packages will be installed into your working directory, without requiring any admin/root priviledges.
Given that conda is available on your system (see `Miniconda <http://conda.pydata.org/miniconda.html>`_), to use the Conda integration, add the `--use-conda` flag to your workflow execution command, e.g. `snakemake --cores 8 --use-conda`.
When `--use-conda` is activated, Snakemake will automatically create software environments for any used wrapper (see above).
Further, you can manually define environments via the `conda` directive, e.g.:

.. code-block:: python

    rule NAME:
        input:
            "table.txt"
        output:
            "plots/myplot.pdf"
        conda:
            "envs/ggplot.yaml"
        script:
            "scripts/plot-stuff.R"

with the following `environment definition <http://conda.pydata.org/docs/using/envs.html#create-environment-file-by-hand>`_:


.. code-block:: yaml

    channels:
     - r
    dependencies:
     - r=3.3.1
     - r-ggplot2=2.1.0

Snakemake will store the environment persistently in ``.snakemake/conda/$hash`` with ``$hash`` being the MD5 hash of the environment definition file content. This way, updates to the environment definition are automatically detected.
Note that you need to clean up environments manually for now. However, they are lightweight and consist only of symlinks to your central conda installation.
