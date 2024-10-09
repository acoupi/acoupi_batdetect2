# Installation

*acoupi_batdetect2* has been designed to run on single-board computer devices like the [Raspberry Pi](https://www.raspberrypi.org/) (RPi).
Users should be able to download and test _acoupi_ software on any Linux-based machine with Python version >=3.8,<3.12 installed.

## Installation Requirements

We recommend the following hardware elements to install and run _acoupi_.

- A Linux-based single board computer such as the Raspberry Pi 4B.
- A SD Card with 64-bit Lite OS version installed.
- A USB ultrasonic Microphone such as an [AudioMoth USB Microphone](https://www.openacousticdevices.info/audiomoth) or an Ultramic 192K/250K.

??? tip "Recommended Hardware"

    The software has been extensively developed and tested with the RPi 4B.
    We advise users to select the RPi 4B or a device featuring similar specifications.

## Installation Steps

??? tip "Getting started with Raspberry Pi"

    If you are new to RPi, we recommend you reading and following the RPi's [**Getting started**](https://www.raspberrypi.com/documentation/computers/getting-started.html) documentation.

To install and use *acoupi_batdetect" on your embedded device follow these steps:

**Step 1:** Install *acoupi_batdetect2* and its dependencies.

!!! Example "CLI Command: install *acoupi_batdetect2*"

    ```bash
    curl -sSL https://github.com/acoupi_batdetect2/install_script.sh | bash
    ```

**Step 2:** Configure the *acoupi_batdetect2* program.

*acoupi_batdetect2* program includes multiple components for recording, processing, saving and deleting audio files, as well as sending detections and summary messages to a remote server. Enter the following command to configure the program according to your needs.

!!! Example "CLI Command: configure *acoupi_batdetect* program"

    ```bash
    acoupi setup --program acoupi_batdetect2.program
    ```

**Step 3:** To start a deployment of *acoupi_batdetect*, run the command:

!!! Example "CLI Command: start the configured *acoupi_batdetect* program"

    ```bash
    acoupi deployment start
    ```

??? tip "Using _acoupi_ from the command line"

    To check what are the available commands for _acoupi_, enter `acoupi --help`. Also look at the [CLI documentation](../reference/cli.md) for further info.