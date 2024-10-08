# acoupi_batdetect2

## What is acoupi_batdetect2?

*acoupi_batdetect2* is an open-source Python package that implement the  BatDetect2 [@macodha and al.](https://doi.org/10.1101/2022.12.14.520490) bioacoustics DL model using the [**acoupi**](https://github.com/acoupi) framework. 

The *acoupi_batdetect2*  provides users with a pre-built _acoupi_ program that can be configured and tailored to their use cases of monitoring UK bats species.

## Requirements

*acoupi_batdetect2* has been designed to run on single-board computer devices like the [Raspberry Pi](https://www.raspberrypi.org/) (RPi).
Users should be able to download and test *acoupi_batdetect2* software on any Linux-based machines with Python version >=3.8,<3.12 installed.

- A Linux-based single board computer such as the Raspberry Pi 4B.
- A SD Card with 64-bit Lite OS version installed.
- An ultrasonic USB Microphone such as an [AudioMoth USB Microphone](https://www.openacousticdevices.info/audiomoth) or an Ultramic 192K/250K.


??? tip "Recommended Hardware"

    The software has been extensively developed and tested with the RPi 4B.
    We advise users to select the RPi 4B or a device featuring similar specifications.

## Installation

To install *acoupi_batdetect2* on your embedded device follow these steps:

!!! Example "Step1: Install *acoupi_batdetect2* and its dependencies"

    ```bash
    curl -sSL https://github.com/acoupi/acoupi_batdetect2/raw/main/scripts/setup.sh | bash
    ```

!!! Example "Step 2: Configure the *acoupi_batdetect2* program."

    ```bash
    acoupi setup --program acoupi_batdetect2.program
    ```

!!! Example "Step 3: Start the *acoupi_batdetect2* program."

    ```bash
    acoupi deployment start
    ```

??? tip "Using acoupi from the command line"

    To check what are the available commands for acoupi, enter `acoupi --help`. Also look at the [CLI documentation](reference/cli.md) for further info.

## What is the acoupi framework? 🚀

`acoupi` simplifies the use and implementation of open-source AI bioacoustics models.

??? warning "Licenses and Usage"

    Before using a pre-trained AI bioacoustic classifier, review its license to ensure it aligns with your intended use.
    `acoupi` programs built with these models inherit the corresponding model licenses.
    For further licensing details, refer to the [FAQ](faq.md#licensing) section.

??? warning "Model Output Reliability"

    Please note that `acoupi_batdetect2` is not responsible for the accuracy or reliability of the model predictions.
    It is crucial to understand the performance and limitations of the model before using it in your project.

    To learn more about the BatDetect2 model architecture and its precision recall, read the publication [_Towards a General Approach for Bat Echolocation Detection and Classification_ by Oisin M.A., et al., 2022](https://doi.org/10.1101/2022.12.14.520490).

## Next steps 📖

Get to know _acoupi_ better by exploring this documentation.

<table>
    <tr>
        <td>
            <a href="tutorials">Tutorials</a>
            <p>Step-by-step information on how to install, configure and deploy <i>acoupi</i> for new users.</p>
        </td>
        <td>
            <a href="how_to_guide">How-to Guides</a>
            <p>Guides to learn how to customise and built key elements of <i>acoupi</i>.</p>
        </td>
    </tr>
    <tr>
        <td>
            <a href="explanation">Explanation</a>
            <p>Learning about the <i>acoupi</i> framework.</p>
        </td>
        <td>
            <a href="reference">Reference</a>
            <p>Technical information refering to <i>acoupi_batdetect2</i> code.</p>
        </td>
    </tr>
</table>

!!! tip "Important"

    We would love to hear your feedback about the documentation. We are always looking to hearing suggestions to improve readability and user's ease of navigation. Don't hesitate to reach out if you have comments!

*[CLI]: Command Line Interface
*[DL]: Deep Learning
*[RPi]: Raspberry Pi
