# XCSoar Topology Generator

## Description

The XCSoar Topology Generator is a tool that generates topology data for use in
XCSoar maps. The project utilizes data from OpenStreetMap (OSM) as its data
source. The extraction process involves using a PostgreSQL database with
PostGIS enabled to import the OSM planet.pbf file. The imported data is then
processed using PostGIS functions to reduce the topology, making it suitable
for use on mobile devices. Finally, the processed data is extracted into
shapefiles that can be used with the map generator.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Features](#features)
- [Contributing](#contributing)
- [License](#license)

## Installation

To install and set up the XCSoar Topology Generator, follow these steps:

1. Copy the `config.ini.example` file located in the `conf` directory to
   `config.ini`.
1. Edit the `config.ini` file and set the values for `user`, `database name`,
   and `password` according to your PostgreSQL database configuration.
1. Install the necessary Python libraries by running `pip install -r
   requirements.txt`.
1. Run the script `./scripts/db_create.sh` to create the database with PostGIS
   extensions.
1. Use the script `./scripts/db_import <pbf>` to import the OSM planet.pbf file
   into the PostGIS database. Replace `<pbf>` with the path to your OSM
   planet.pbf file. **Note:** This process can take a considerable amount of time,
   potentially up to a week depending on the size of the PBF file.
1. Once the import process is complete, you can use the scripts
   `./scripts/reduce_*` to filter and simplify the topology based on your
   requirements. Choose the appropriate script for your use case.
1. Finally, use the scripts `./scripts/export_*` to generate shapefiles in the
   output directory. Again, choose the appropriate script for your desired
   output.

**Warning:** Importing and processing the OSM planet.pbf file is a
resource-intensive process. Please ensure that your machine meets the following
minimum requirements:

- At least 32 GB of RAM
- 1 TB of disk space

## Usage

To use the XCSoar Topology Generator, follow the installation instructions
mentioned above. After completing the installation steps, you can proceed with
the following usage instructions:

1. Configure the `config.ini` file in the `conf` directory with the necessary
   database credentials.
1. Import the OSM planet.pbf file into the PostGIS database using the
   `./scripts/db_import` script. Provide the path to the PBF file as a
   parameter.
1. Run the appropriate `./scripts/reduce_*` script to filter and simplify the
   topology based on your requirements.
1. Generate shapefiles by executing the corresponding `./scripts/export_*`
   script. The shapefiles will be saved in the output directory.

Note: Be aware that the import process can be time-consuming, and the reduction
and export steps might require substantial computational resources depending on
the size of the dataset.

## Features

- Import OpenStreetMap data from the OSM planet.pbf file into a PostgreSQL
  database with PostGIS extensions.
- Process and reduce the topology of the imported data using the provided
  scripts for filtering and simplification.
- Generate shapefiles from the processed data, suitable for use with the XCSoar
  map generator.
- [Include any additional features or functionalities of the project.]

## Contributing

Contributions to the XCSoar Topology Generator are welcome! If you would like
to contribute, please follow these guidelines:

1. Fork the repository and create a new branch for your contribution.
1. Make your changes and ensure that the code is properly tested.
1. Submit a pull request, clearly describing the changes you've made and the
   purpose of your contribution.

## License

The XCSoar Topology Generator is open source software licensed under the
[GPL-2.0-or-later](LICENSE) license. Feel free to use, modify, and distribute
the project according to the terms of the license.
