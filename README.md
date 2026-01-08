# MOSuite-Galaxy

<!-- README.md is generated from README.qmd. Please edit that file -->

Galaxy workflow configuration for
[MOSuite](https://github.com/CCBR/MOSuite)

<figure>
<a
href="https://github.com/CCBR/MOSuite-Galaxy/actions/workflows/build-python.yml"><img
src="https://github.com/CCBR/MOSuite-Galaxy/actions/workflows/build-python.yml/badge.svg" /></a>
</figure>

## Installation

```bash
pip install git+https://github.com/CCBR/MOSuite-Galaxy
```

## Usage

```bash
galaxysynth --help
```

    usage: galaxysynth [-h] [-o OUTPUT] [--docker DOCKER] [--debug] [-v] blueprint

    Generate Galaxy tool XML from SPAC blueprint JSON files with sanitizer and
    section support

    positional arguments:
      blueprint             Path to blueprint JSON file or pattern (e.g.,
                            'template_json_*.json')

    options:
      -h, --help            show this help message and exit
      -o OUTPUT, --output OUTPUT
                            Output directory for XML files (default: galaxy_tools)
      --docker DOCKER       Docker image name (default: spac:mvp)
      --debug               Enable debug output
      -v, --version         show program's version number and exit

```bash
galaxysynth  "templates/2_blueprints/*.json" --docker nciccbr/mosuite:latest --outdir templates/3_galaxy-tools
```
