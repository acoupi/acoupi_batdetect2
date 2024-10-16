# Technical Reference

The _technical reference_ section of _acoupi_batdetect2_ provides detailed information a
on the three essential elements that define the program: the configuration schema, the model, 
and the program itself.

- [Configuration](configuration.md): The configuration schema defines the structure and data types of each configuration variable. It allows users to customise how the _acoupi_batdetect2_ program runs and executes. 

- [Model](model.md): The model is the core of the _acoupi_batdetect2_ program. It handles how the `BatDetect2` model is loaded, how it processes recordings, retrieves detections, and formats the results into a usable format for the subsequent tasks in the program.

- [Program](program.md): The program class encapsulates all essential elements, enabling successful execution on a device. It leverages pre-defined _acoupi_ templates to facilitate the organisation and configuration of the specific tasks and compoments. 

!!! Tip "Learn more about program tasks and compoments:"

    The elements of the _acoupi_batdetect2_ program build and inherit from [_acoupi_](https://acoupi.github.io/acoupi/reference) package. For detailed information on each module, class, and method, refer to the _acoupi_ documentation's reference section.

<table>
  <tr>
    <td>
      <a href="configuration">Configuration</a>
    </td>
    <td>
      <p>The blueprint for customising the _acoupi_batdetect2_ program.</p>
    </td>
  </tr>
  <tr>
    <td>
      <a href="model">Model</a>
    </td>
    <td>
      <p>Configuring the BatDetect2 model to process recordings.</p>
    </td>
  </tr>
  <tr>
    <td>
      <a href="Program">Program</a>
    </td>
    <td>
      <p>Complete unit adapting to users configurations.</p>
    </td>
  </tr>
</table>
