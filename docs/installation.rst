Installation
============

Run DASDC on Linux x86-64. **TensorFlow is the default backend**;
**PyTorch is an optional backend**. Both support CPU and GPU execution.
Follow the TensorFlow setup below, or choose the :ref:`pytorch-backend`.

Requirements
------------
.. list-table::
   :header-rows: 1
   :widths: 28 72

   * - Component
     - Requirement / recommendation
   * - Python package and CLI
     - Python 3.8 or newer.
   * - Default backend
     - TensorFlow 2.7 with Python 3.8–3.9.
   * - Optional backend
     - PyTorch 2.2 or newer; see :ref:`pytorch-backend` for an installation example.
   * - GPU execution
     - A compatible NVIDIA GPU, driver and backend-specific CUDA libraries. See :ref:`tensorflow-gpu` or the CUDA example in :ref:`pytorch-backend`.
   * - Hardware
     - At least 8 CPU cores, 18 GB memory and 200 GB disk are recommended for the workflow.
   * - Simulator
     - The clone includes a compiled ``discoal`` executable. See :doc:`workflow/simu` if you need to recompile it.


1. Clone the repository
-----------------------

.. code-block:: bash

   git clone --branch feat/cli-pytorch \
       https://github.com/soo-h/DASweepDetect.git
   cd DASweepDetect

These instructions describe the ``feat/cli-pytorch`` branch, which contains
the installed ``dasdc`` CLI and optional PyTorch backend used in this guide.

2. Create an environment
------------------------

The default **TensorFlow 2.7 backend requires Python 3.8–3.9**. Install a
compatible interpreter before creating the environment (Python 3.8 shown
here). To use PyTorch instead, replace Steps 2–3 with :ref:`pytorch-backend`.

.. code-block:: bash

   python3.8 -m venv .venv/tensorflow
   source .venv/tensorflow/bin/activate
   python --version

3. Install DASDC
----------------

In the activated Python 3.8–3.9 environment:

.. code-block:: bash

   python -m pip install -e .

.. important::

   This is an editable installation. It calls scripts and the ``discoal``
   executable inside the clone. Keep the repository in place; reinstall
   DASDC if you move it.

4. Enable the simulator and check the CLI
-----------------------------------------

.. code-block:: bash

   chmod 755 discoal
   dasdc --help
   dasdc train --help

Every command can also be invoked as ``python -m dasdc <command>``.

Next, :doc:`detect selective sweeps from scratch <workflow/overview>` or
:ref:`detect selective sweeps with an existing model <two-step-workflow>`.

.. _tensorflow-gpu:

GPU with TensorFlow
-------------------

The default TensorFlow 2.7 backend supports GPU execution. With a
compatible GPU and its required libraries available, TensorFlow
automatically places supported operations on the GPU during training and
prediction. No additional DASDC command-line option is needed. See the
`TensorFlow GPU guide <https://www.tensorflow.org/guide/gpu>`_.

For TensorFlow 2.7, the `official tested configuration
<https://www.tensorflow.org/install/source#gpu>`_ uses **CUDA 11.2 and
cuDNN 8.1**. These libraries and a compatible NVIDIA driver must be
available to the TensorFlow environment. Check which GPUs it can see:

.. code-block:: bash

   python - <<'PY'
   import tensorflow as tf
   print(tf.config.list_physical_devices("GPU"))
   PY

An empty list means TensorFlow cannot see a usable GPU in that environment.

.. _pytorch-gpu:
.. _optional-gpu-with-pytorch:
.. _pytorch-backend:

Optional: PyTorch backend
-------------------------

Choose PyTorch as an alternative training and prediction backend. It
supports both CPU and GPU execution. From the repository root, create a
separate environment in place of Steps 2–3. If another environment is
active, run ``deactivate`` first.

The following GPU installation example uses Python 3.11, PyTorch 2.2.2
and CUDA 12.1:

.. code-block:: bash

   python3.11 -m venv .venv/pytorch
   source .venv/pytorch/bin/activate
   python -m pip install "torch==2.2.2" \
       --index-url https://download.pytorch.org/whl/cu121
   python -m pip install -e . "numpy<2"

Use the `official PyTorch installation selector
<https://pytorch.org/get-started/locally/>`_ for a different Python or CUDA
combination. Keep **NumPy below 2 for the PyTorch 2.2.2 example**; see the
`PyTorch NumPy compatibility discussion
<https://github.com/pytorch/pytorch/issues/107302>`_. Then complete Step 4.

.. note::

   Select PyTorch with ``--backend pytorch`` in the :doc:`training
   <workflow/train>` and :doc:`prediction <workflow/pred>` commands. For GPU
   execution, also add ``--device cuda``. Use the same workflow inputs and
   the default training settings. Train and predict with the same backend;
   existing TensorFlow models require TensorFlow for prediction.

Optional: legacy dependency archive
-----------------------------------

If pip installation fails, ``DASDC_dependency.tar.gz`` is available from
`Mendeley Data <https://data.mendeley.com/datasets/vdg2nbpc4j>`_. It contains
legacy, platform-specific packages for a compatible Linux x86-64 Python 3.8
environment. Find the active environment's package directory with:

.. code-block:: bash

   python -c \
       "import sysconfig; print(sysconfig.get_paths()['purelib'])"

Do not extract the archive into the shell's ``PATH`` value.
