.. _install-from-conda:

Installing ARTIQ
================

The preferred way of installing ARTIQ is through the use of the conda package manager.
The conda package contains pre-built binaries that you can directly flash to your board.

.. warning::
    NIST users on Linux need to pay close attention to their ``umask``.
    The sledgehammer called ``secureconfig`` leaves you (and root) with umask 027 and files created by root (for example through ``sudo make install``) inaccessible to you.
    The usual umask is 022.


.. warning::
    Conda packages are supported for Linux (64-bit) and Windows (64-bit).
    Users of other operating systems (32-bit Linux or Windows, BSD, OSX ...) should and can :ref:`install from source <install-from-source>`.

.. _install-anaconda:

Installing Anaconda or Miniconda
--------------------------------

You can either install Anaconda from https://www.anaconda.com/download/ or install the more minimalistic Miniconda from https://conda.io/miniconda.html

After installing either Anaconda or Miniconda, open a new terminal (also known as command line, console, or shell and denoted here as lines starting with ``$``) and verify the following command works::

    $ conda

Executing just ``conda`` should print the help of the ``conda`` command [1]_.

Installing the ARTIQ packages
-----------------------------

.. note::
    On a system with a pre-existing conda installation, it is recommended to update conda to the latest version prior to installing ARTIQ.

Add the M-Labs ``main`` Anaconda package repository containing stable releases and release candidates::

    $ conda config --prepend channels m-labs

.. note::
    To use the development versions of ARTIQ, also add the ``dev`` label (m-labs/label/dev).
    Development versions are built for every change and contain more features, but are not as well-tested and are more likely to contain more bugs or inconsistencies than the releases in the default ``main`` label.

Add the conda-forge repository containing ARTIQ dependencies to your conda configuration::

    $ conda config --add channels conda-forge

Then prepare to create a new conda environment with the ARTIQ package and the matching binaries for your hardware:
choose a suitable name for the environment, for example ``artiq-main`` if you intend to track the main label, ``artiq-3`` for the 3.x release series, or ``artiq-2016-04-01`` if you consider the environment a snapshot of ARTIQ on 2016-04-01.
Choose the package containing the binaries for your hardware:

    * ``artiq-kc705-nist_clock`` for the KC705 board with the NIST "clock" FMC backplane and AD9914 DDS chips.
    * ``artiq-kc705-nist_qc2`` for the KC705 board with the NIST QC2 FMC backplane and AD9914 DDS chips.

Conda will create the environment, automatically resolve, download, and install the necessary dependencies and install the packages you select::

    $ conda create -n artiq-main artiq-kc705-nist_clock

After the installation, activate the newly created environment by name.
On Unix::

    $ source activate artiq-main

On Windows::

    $ activate artiq-main

This activation has to be performed in every new shell you open to make the ARTIQ tools from that environment available.

.. note::
    Some ARTIQ examples also require matplotlib and numba, and they must be installed manually for running those examples. They are available in conda.


Upgrading ARTIQ
---------------

When upgrading ARTIQ or when testing different versions it is recommended that new environments are created instead of upgrading the packages in existing environments.
Keep previous environments around until you are certain that they are not needed anymore and a new environment is known to work correctly.
You can create a new conda environment specifically to test a certain version of ARTIQ::

    $ conda create -n artiq-test-1.0rc2 artiq-kc705-nist_clock=1.0rc2

Switching between conda environments using ``$ source deactivate artiq-1.0rc2`` and ``$ source activate artiq-1.0rc1`` is the recommended way to roll back to previous versions of ARTIQ.
You can list the environments you have created using::

    $ conda env list

See also the `conda documentation <http://conda.pydata.org/docs/using/envs.html>`_ for managing environments.

Preparing the core device FPGA board
------------------------------------

You now need to write three binary images onto the FPGA board:

1. The FPGA gateware bitstream
2. The BIOS
3. The ARTIQ runtime

They are all shipped in the conda packages, along with the required flash proxy gateware bitstreams.

.. _install-openocd:

Installing OpenOCD
^^^^^^^^^^^^^^^^^^

OpenOCD can be used to write the binary images into the core device FPGA board's flash memory.
The ``artiq`` or ``artiq-dev`` conda packages install ``openocd`` automatically but it can also be installed explicitly using conda on both Linux and Windows::

    $ conda install openocd

.. _setup-openocd:

Configuring OpenOCD
^^^^^^^^^^^^^^^^^^^

Some additional steps are necessary to ensure that OpenOCD can communicate with the FPGA board.

On Linux, first ensure that the current user belongs to the ``plugdev`` group (i.e. `plugdev` shown when you run `$ groups`). If it does not, run ``sudo adduser $USER plugdev`` and relogin. If you installed OpenOCD using conda and are using the conda environment ``artiq-main``, then execute the statements below. If you are using a different environment, you will have to replace ``artiq-main`` with the name of your environment::

    $ sudo cp ~/.conda/envs/artiq-main/share/openocd/contrib/60-openocd.rules /etc/udev/rules.d
    $ sudo udevadm trigger

if you installed it from source:: Assuming you installed OpenOCD in ``/usr/local``, otherwise please substitute the install directory::

    $ sudo cp /usr/local/share/openocd/contrib/60-openocd.rules /etc/udev/rules.d
    $ sudo udevadm trigger

On Windows, a third-party tool, `Zadig <http://zadig.akeo.ie/>`_, is necessary. Use it as follows:

1. Make sure the FPGA board's JTAG USB port is connected to your computer.
2. Activate Options → List All Devices.
3. Select the "Digilent Adept USB Device (Interface 0)" or "FTDI Quad-RS232 HS" (or similar)
   device from the drop-down list.
4. Select WinUSB from the spinner list.
5. Click "Install Driver" or "Replace Driver".

You may need to repeat these steps every time you plug the FPGA board into a port where it has not been plugged into previously on the same system.

.. _flashing-core-device:

Flashing the core device
^^^^^^^^^^^^^^^^^^^^^^^^

Then, you can flash the board:

* For the KC705 board (selecting the appropriate hardware peripheral)::

    $ artiq_flash -t kc705 -V [nist_clock/nist_qc2]

  The SW13 switches also need to be set to 00001.

The next step is to flash the MAC and IP addresses to the board. See :ref:`those instructions <flash-mac-ip-addr>`.

.. _configuring-core-device:

Configuring the core device
---------------------------

This should be done after either installation method (conda or source).

* (optional) If you are using DRTIO and the default routing table (for a star topology) is not suitable to your needs, prepare the routing table and add it to the ``flash_storage.img`` created in the next step. The routing table can be easily changed later, so you can skip this step if you are just getting started and only want to test local channels. See :ref:`Using DRTIO <using-drtio>`.

.. _flash-mac-ip-addr:

* Set the MAC and IP address in the :ref:`core device configuration flash storage <core-device-flash-storage>` (see above for the ``-t`` and ``-V`` options to ``artiq_flash`` that may be required): ::

    $ artiq_mkfs flash_storage.img -s mac xx:xx:xx:xx:xx:xx -s ip xx.xx.xx.xx
    $ artiq_flash -t [board] -V [adapter] -f flash_storage.img storage start

* (optional) Flash the idle kernel

The idle kernel is the kernel (some piece of code running on the core device) which the core device runs whenever it is not connected to a PC via Ethernet.
This kernel is therefore stored in the :ref:`core device configuration flash storage <core-device-flash-storage>`.
To flash the idle kernel:

        * Compile the idle experiment:
                The idle experiment's ``run()`` method must be a kernel: it must be decorated with the ``@kernel`` decorator (see :ref:`next topic <connecting-to-the-core-device>` for more information about kernels).

                Since the core device is not connected to the PC, RPCs (calling Python code running on the PC from the kernel) are forbidden in the idle experiment.
                ::

                $ artiq_compile idle.py

        * Write it into the core device configuration flash storage: ::

                $ artiq_coremgmt config -f idle_kernel idle.elf

.. note:: You can find more information about how to use the ``artiq_coremgmt`` utility on the :ref:`Utilities <core-device-management-tool>` page.

* (optional) Flash the startup kernel

The startup kernel is executed once when the core device powers up. It should initialize DDSes, set up TTL directions, etc. Proceed as with the idle kernel, but using the ``startup_kernel`` key in the ``artiq_coremgmt`` command.

For DRTIO systems, the startup kernel should wait until the desired destinations (including local RTIO) are up, using :meth:`artiq.coredevice.Core.get_rtio_destination_status`.

* (optional) Select the RTIO clock source

Some core devices may use either an external clock signal or their internal clock. The clock is selected at power-up. Use one of these commands: ::

    $ artiq_coremgmt config write -s rtio_clock i  # internal clock (default)
    $ artiq_coremgmt config write -s rtio_clock e  # external clock


.. rubric:: Footnotes

.. [1] [Linux] If your shell does not find the ``conda`` command, make sure that the conda binaries are in your ``$PATH``:
       If ``$ echo $PATH`` does not show the conda directories, add them: execute ``$ export PATH=$HOME/miniconda3/bin:$PATH`` if you installed conda into ``~/miniconda3``.
