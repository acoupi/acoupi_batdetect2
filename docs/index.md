# acoupi_batdetect2

## What is acoupi_batdetect2?

*acoupi_batdetect2* is an open-source Python package that implement the [BatDetect2](https://github.com/macaodha/batdetect2) bioacoustic deep-learning model on edge devices like the RaspberryPi using the [_acoupi_](https://github.com/acoupi) framework. The BatDetect2 DL model has been developed by [Oisin M.A., et al.](https://doi.org/10.1101/2022.12.14.520490) to detect and classify UK bats species. 

!!! Warning "What is the difference between _acoupi_ and _acoupi_batdetect2_?"

    __acoupi_batdetect2__ and [___acoupi___](https://acoupi.github.io/acoupi) are different. The __acoupi_batdetect2__ program is built on top of the ___acoupi___ python package. Think of ___acoupi___ like a bag of LEGO pieces that you can assemble into multiple shapes and forms. __acoupi_batdectect2__ would be the results of assembling some of these LEGO pieces into a "bat"!

??? Tip "Get familiar with _acoupi_"

    *acoupi_batdetect2* builds on and inherits features from _acoupi_. If you want to learn more the [_acoupi_](https://acoupi.github.io/acoupi) framework, we recommand starting with _acoupi's_ home documentation. 

## Requirements

*acoupi_batdetect2* is designed to run on single-board computers like the Raspberry Pi.
It can be installed and tested on any Linux-based machines with Python version >=3.8,<3.12.

- A Linux-based single-board computer such as the Raspberry Pi 4B.
- A SD Card with the 64-bit Lite OS version installed.
- An ultrasonic USB Microphone, such as an [AudioMoth USB Microphone](https://www.openacousticdevices.info/audiomoth) or an Ultramic 192K/250K.


??? tip "Recommended Hardware"

    The software has been extensively developed and tested with the RPi 4B.
    We advise users to select the RPi 4B or a device featuring similar specifications.

## Installation

To install *acoupi_batdetect2* on your embedded device, you will need to first have _acoupi_ installed on your device. Follow these steps to install both _acoupi_ and _acoupi_batdetect2_:

!!! Example "Step1: Install _acoupi_ and its dependencies"

    ```bash
    curl -sSL https://github.com/acoupi/acoupi/raw/main/scripts/setup.sh | bash
    ```

!!! Example "Step2: Install *acoupi_batdetect2* and its dependencies"

    ```bash
    pip install acoupi_batdetect2
    ```

!!! Example "Step 3: Configure the *acoupi_batdetect2* program."

    ```bash
    acoupi setup --program acoupi_batdetect2.program
    ```

!!! Example "Step 4: Start the *acoupi_batdetect2* program."

    ```bash
    acoupi deployment start
    ```

??? tip "Using _acoupi_batdetect2_ from the command line"

    To check what are the available commands for _acoupi_batdetect2_, enter `acoupi --help`. For more details about each of the commands, refer to the _acoupi_ [CLI documentation](https://acoupi.github.io/acoupi/reference/cli/) for further info.

## What is acoupi? 🚀

_acoupi_ is an open-source Python package that simplifies the use and implementation of bioacoustic classifiers on edge devices. 
It integrates and standardises the entire bioacoustic monitoring workflow, facilitating the creation of custom sensors, by handling audio recordings, processing, classifications, detections, communication, and data management.

!!! warning "Licenses and Usage"

    **_acoupi_batdetect2_ can not be used for commercial purposes.**

    The *acoupi_batdetect2* program inherits the BatDetect2 model license, published under the [__Creative Commons Attribution-NonCommercial 4.0 International__](https://github.com/macaodha/batdetect2?tab=License-1-ov-file#readme). Please make sure to review this license to ensure your intended use complies with its terms.

!!! warning "Model Output Reliability"

    Please note that *acoupi_batdetect2* program is not responsible for the accuracy or reliability of predictions made by the BatDetect2 model. It is essential to understand the model's performance and limitations before using it in your project.

    For more details on the BatDetect2 model architecture, as well as its precision and recall, refer to the publication [Mac Aodha O., et al., (2002) _Towards a General Approach for Bat Echolocation Detection and Classification_](https://doi.org/10.1101/2022.12.14.520490).

!!! Tip "Available _acoupi_ programs!"

    _acoupi_ offers various programs that can be configured to meet your needs. These programs can be used to simply record audio, send messages, or even detect and classify birds species. Check out the full list of available [_acoupi_ programs](https://acoupi.github.io/acoupi/explanation/programs/#pre-built_programs) to learn more. 


## Next steps 📖

Get to know _acoupi_ better by exploring this documentation.

<table>
    <tr>
        <td>
            <a href="tutorials">Tutorials</a>
            <p>Step-by-step information on how to install, configure and deploy <i>acoupi_batdetect2</i> for new users.</p>
        </td>
    </tr>
    <tr>
        <td>
            <a href="explanation">Explanation</a>
            <p>Learn more about the building blocks constituing <i>acoupi_batdetect2</i> program.</p>
        </td>
    </tr>
    <tr>
        <td>
            <a href="reference">Reference</a>
            <p>Technical information refering to <i>acoupi_batdetect2</i> code.</p>
        </td>
    </tr>
</table>

!!! tip "Important"

    We would love to hear your feedback about the documentation. We are always looking to hearing suggestions to improve readability and user's ease of navigation. Don't hesitate to reach out if you have comments!

*[AI]: Artificial Intelligence
*[CLI]: Command Line Interface
*[DL]: Deep Learning
*[RPi]: Raspberry Pi
