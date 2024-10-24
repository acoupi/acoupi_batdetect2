# acoupi_batdetect2
An acoupi-compatible BatDetect2 model and program

> [!TIP]
> Read the latest [documentation](https://acoupi.github.io/acoupi_batdetect2/)

#### Readme Content
- [What is acoupi_batdetect2?](#what-is-acoupi_batdetect2)
- [What is the difference between _acoupi_ and _acoupi_batdetect2_](#what-is-the-difference-between-acoupi-and-acoupi_batdetect2)
- [Requirements](#requirements)
- [Installation](#installation)
- [What is acoupi?](#what-is-acoupi)

## What is _acoupi_batdetect2_?
*acoupi_batdetect2* is an open-source Python package that implement the [BatDetect2](https://github.com/macaodha/batdetect2) bioacoustic deep-learning model on edge devices like the [Raspberry Pi](https://www.raspberrypi.org/), using the [_acoupi_](https://acoupi.github.io/acoupi) framework. The BatDetect2 DL model has been developed by [Mac Aodha O., et al.](https://doi.org/10.1101/2022.12.14.520490) to detect and classify UK bats species. 

## What is the difference between _acoupi_ and _acoupi_batdetect2_?

__acoupi_batdetect2__ and [___acoupi___](https://acoupi.github.io/acoupi) are different. The __acoupi_batdetect2__ program is built on top of the ___acoupi___ python package. Think of ___acoupi___ like a bag of LEGO pieces that you can assemble into multiple shapes and forms. __acoupi_batdectect2__ would be the results of assembling some of these LEGO pieces into a "bat"!

> [!TIP]
> **Get familiar with _acoupi_**
>
> *acoupi_batdetect2* builds on and inherits features from _acoupi_. If you want to learn more the [_acoupi_](https://acoupi.github.io/acoupi) framework, we recommand starting with _acoupi's_ home documentation. 

## Requirements
_acoupi_ has been designed to run on single-board computer devices like the [Raspberry Pi](https://www.raspberrypi.org/) (RPi).
Users should be able to download and test _acoupi_ software on any Linux-based machines with Python version >=3.8,<3.12 installed.

- A Linux-based single board computer such as the Raspberry Pi 4B. 
- A SD Card with 64-bit Lite OS version installed.
- A USB Microphone such as an AudioMoth, a µMoth, an Ultramic 192K/250K.

> [!TIP] 
> **Recommended Hardware**
>
> The software has been extensively developed and tested with the RPi 4B. We advise users to select the RPi 4B or a device featuring similar specifications.

## Installation

To install *acoupi_batdetect2* on your embedded device, you will need to first have _acoupi_ installed on your device. Follow these steps to install both _acoupi_ and _acoupi_batdetect2_:


**Step 1:** Install _acoupi_ and its dependencies. 
```bash
curl -sSL https://github.com/acoupi/acoupi/raw/main/scripts/setup.sh | bash
```

**Step 2:** Install *acoupi_batdetect2* and its dependencies

```bash
pip install acoupi_batdetect2
```

**Step 3:** Configure the *acoupi_batdetect2* program.

```bash
acoupi setup --program acoupi_batdetect2.program
```

**Step 4**: Start the *acoupi_batdetect2* program.

```bash
acoupi deployment start
```

> [!TIP] 
> To check what are the available commands for acoupi, enter `acoupi --help`.


## What is acoupi?

_acoupi_ is an open-source Python package that simplifies the use and implementation of bioacoustic classifiers on edge devices. 
It integrates and standardises the entire bioacoustic monitoring workflow, facilitating the creation of custom sensors, by handling audio recordings, processing, classifications, detections, communication, and data management.

> [!WARNING] 
> **Licenses and Usage**
>
>**_acoupi_batdetect2_ can not be used for commercial purposes.** 
>
>  The *acoupi_batdetect2* program inherits the BatDetect2 model license, published under the [__Creative Commons Attribution-NonCommercial 4.0 International__](https://github.com/macaodha/batdetect2?tab=License-1-ov-file#readme). Please make sure to review this license to ensure your intended use complies with its terms.

> [!WARNING]
> **Model Output Reliabilit**
>
> Please note that *acoupi_batdetect2* program is not responsible for the accuracy or reliability of predictions made by the BatDetect2 model. It is essential to understand the model's performance and limitations before using it in your project.
> 
> For more details on the BatDetect2 model architecture, as well as its precision and recall, refer to the publication [Mac Aodha O., et al., (2002) _Towards a General Approach for Bat Echolocation Detection and Classification_](https://doi.org/10.1101/2022.12.14.520490).

> [!IMPORTANT]
> We would love to hear your feedback about the documentation. We are always looking to hearing suggestions to improve readability and user's ease of navigation. Don't hesitate to reach out if you have comments!
