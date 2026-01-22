# MOSuite-Galaxy

<!-- README.md is generated from README.qmd. Please edit that file -->

Galaxy workflow configuration for
[MOSuite](https://github.com/CCBR/MOSuite)

[![](https://github.com/CCBR/MOSuite-Galaxy/actions/workflows/build-python.yml/badge.svg)](https://github.com/CCBR/MOSuite-Galaxy/actions/workflows/build-python.yml)

MOSuite Workflow on Galaxy:
<http://k8s-galaxy-b671dd4f69-710212292.us-east-1.elb.amazonaws.com/u/kelly-sovacool/w/mosuite>

## Installation

```bash
pip install git+https://github.com/CCBR/MOSuite-Galaxy
```

## Usage

```bash
galaxysynth --help
```

    usage: galaxysynth [-h] [-o OUTPUT] [--docker DOCKER] [--citation CITATION]
                       [--debug] [-v]
                       blueprint

    Generate Galaxy tool XML from blueprint JSON files with sanitizer and section
    support

    positional arguments:
      blueprint             Path to blueprint JSON file or pattern (e.g.,
                            'template_json_*.json')

    options:
      -h, --help            show this help message and exit
      -o OUTPUT, --output OUTPUT
                            Output directory for XML files (default: galaxy_tools)
      --docker DOCKER       Docker image name (default: nciccbr/mosuite:latest)
      --citation CITATION   Citation DOI (default: 10.5281/zenodo.16371580)
      --debug               Enable debug output
      -v, --version         show program's version number and exit

```bash
galaxysynth  "templates/2_blueprints/*.json" \
    --docker nciccbr/mosuite:v0.2.1 \
    --output templates/3_galaxy-tools
```

## Developer notes

- Please view the [contributing guide](.github/CONTRIBUTING.md) before
  opening a pull request.
- Galaxy Tool XML documentation:
  <https://docs.galaxyproject.org/en/master/dev/schema.html>
