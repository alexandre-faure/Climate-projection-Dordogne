# Climate Modeling of Dordogne, France

[![License](https://img.shields.io/badge/license-GPLv3-blue.svg)](https://opensource.org/license/gpl-3-0)

## Overview

This project aims to analyse future evolutions of the climate of the Dordogne region in France. It relies on IPCC models from CMIP6 for ssp245 and ssp585. This work was executed for the NGO [0.6 Planète](https://www.06planet.org/fr/), which is planning to build a resilient eco-village with a sustainable ecological footprint in collaboration with the [Université Paris Saclay](http://www.universite-paris-saclay.fr/objets-interdisciplinaires/alliance-climate-action-now). This work is one of the deliverables that support our recommandations in terms of urbanism and technical solutions.

<div align="center">
<img src="https://www.universite-paris-saclay.fr/sites/default/files/styles/max_325x325/public/2022-02/logo-allcan.png?itok=BPJUh5dQ" alt="Logo of AllACN, University of Paris Saclay" width=120px>
    &nbsp; & &nbsp;
<img src="https://www.06planet.org/wp-content/uploads/2021/06/cropped-logo-0.6planet-1.png" alt="Logo of 0.6 Planète" width=200 style="background-color:white; margin-right:50px;">
</div>

## Features

- Data collection and preprocessing
- Climate model bias removing
- Climate projections and scenario analysis
- Visualization of results

## Installation

1. Clone the repository:

    ```shell
    git clone git@github.com:alexandre-faure/Climate-projection-Dordogne.git
    ```

2. Install the required dependencies:

    ```shell
    pip install -r requirements.txt
    ```

## Usage

1. Prepare the data:

    - Download climate data for the Dordogne region.
    - Preprocess the data to keep the desired variables, time period and position.

2. Unskew the data:

    - Unskew the climate model outputs using the provided scripts, based on meteorological station data.

4. Analyze the results:

    - Visualize the model outputs using the provided scripts.
    - Interpret the results and draw conclusions.

## License

This project is licensed under the [GNU General Public License](LICENSE).

## Contact

For any questions or inquiries, please contact [alexandre.faure@student-cs.fr](mailto:alexandre.faure@student-cs.fr).
