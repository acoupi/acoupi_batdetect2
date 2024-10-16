# Installation

*acoupi_batdetect2* has been designed to run on single-board computer devices like the [Raspberry Pi](https://www.raspberrypi.org/) (RPi).
Users should be able to download and test _acoupi_batdetect2_ on any Linux-based machine with [_acoupi_](https://pypi.org/project/acoupi/0.1.0/) software and Python version >=3.8,<3.12 installed.

## Installation Requirements

We recommend the following hardware elements to install and run _acoupi_batdetect2_.

- A Linux-based single-board computer such as the Raspberry Pi 4B.
- A SD Card with 64-bit Lite OS version installed.
- A USB ultrasonic Microphone such as an [AudioMoth USB Microphone](https://www.openacousticdevices.info/audiomoth) or an Ultramic 192K/250K.

??? tip "Recommended Hardware"

    The software has been extensively developed and tested with the RPi 4B.
    We advise users to select the RPi 4B or a device featuring similar or higher specifications.

## Installation Steps

??? tip "Getting started with Raspberry Pi"

    If you are new to RPi, we recommend you reading and following the RPi's [**Getting started**](https://www.raspberrypi.com/documentation/computers/getting-started.html) documentation.

To install and use _acoupi_batdetect2_ on your embedded device follow these steps:

**Step 1:** Install _acoupi_ and its dependencies.

!!! Example "CLI Command: install _acoupi_"

    ```bash
    curl -sSL https://github.com/acoupi/acoupi/raw/main/scripts/setup.sh | bash
    ```

**Step 2:** Install _acoupi_batdetect2_.

!!! Example "CLI Command: install _acoupi_batdetect2_"

    ```bash
    pip install acoupi_batdetect2
    ```


**Step 3:** Configure the *acoupi_batdetect2* program.

*acoupi_batdetect2* program includes multiple components for recording, processing, saving and deleting audio files, as well as sending detections and summary messages to a remote server. Enter the following command to configure the program according to your needs.

!!! Example "CLI Command: configure *acoupi_batdetect* program"

    ```bash
    acoupi setup --program acoupi_batdetect2.program
    ```

**Step 4:** To start a deployment of *acoupi_batdetect2*, run the command:

!!! Example "CLI Command: start the configured *acoupi_batdetect* program"

    ```bash
    acoupi deployment start
    ```