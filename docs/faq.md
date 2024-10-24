# FAQ

#### What is acoupi-batdetect2? 
**acoupi-batdetect2** is the implementation of the AI Bioacoustic Classifier [BatDetect2](https://github.com/macaodha/batdetect2/tree/main) using acoupi Python toolkit. 

## What is BatDetect2? 
**BatDetect2** is a deep-learning model to detect and classify bat echolocation calls in high frequency audio recordings. 

The model was developed by Santiago Martinez Balvanera ([@mbsantiago](https://github.com/mbsantiago)) and Oisin Mac Adoha ([@macaodha](https://github.com/macaodha)). 

## Can the BatDetect2 model classify any bat species? 
No, the BatDetect2 model was developed for UK bat species. When using the model to classifiy bat species not found in the UK, you will most probably get misclassification. 

## For who is _acoupi_batdetect2_? 
_acoupi_batdetect2_ is itended for researchers, practioners, and individuals interested in recording and classifying UK bat species. 

## Can I configure _acoupi_batdetect2_?

Yes. Users can customised the configuration parameters of _acoupi-batdetect2_ to suit their own needs. See [tutorials/configuration](tutorials/configuration.md) to learn more about the configuration options.

## What are the requirements to use _acoupi_batdetect2_?
To use _acoupi-batdetect2_ you will need the following hardware:

 - a Raspberry Pi 4
 - an SD Card (32GB or 64GB) with RaspbiOS-Arm64-Lite installed. 
 - a USB microphone being able to record high-frequencies such as the [AudioMoth](https://www.openacousticdevices.info/audiomoth) or the [Ultramic](https://www.dodotronic.com/product/ultramic-um192k/) from Dodotronic. 

## Where can I found more information about BatDetect2? 

1. The [BatDetect2 GitHub repository](https://github.com/macaodha/batdetect2/tree/main) contains a lot of information about the model. You may also want to check the [PyPi documentation](https://pypi.org/project/batdetect2/). 

2. The research article ["Towards a Genera Approach for Bat Echolocation Detection and Classification"](https://www.biorxiv.org/content/biorxiv/early/2022/12/16/2022.12.14.520490.full.pdf) (Mac Aodha et al. 2022) is also a great resource to learn more about the architecture and performance of the model. 
