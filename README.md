# MOSuite-Galaxy

<!-- README.md is generated from README.qmd. Please edit that file -->

Galaxy workflow configuration for
[MOSuite](https://github.com/CCBR/MOSuite)

[![](https://github.com/CCBR/MOSuite-Galaxy/actions/workflows/build-python.yml/badge.svg)](https://github.com/CCBR/MOSuite-Galaxy/actions/workflows/build-python.yml)
[![codecov](https://codecov.io/gh/CCBR/MOSuite-Galaxy/graph/badge.svg?token=QV46CjB0Bg)](https://codecov.io/gh/CCBR/MOSuite-Galaxy)

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
                       [--repo-name REPO_NAME] [--cli-command CLI_COMMAND]
                       [--pkg-name PKG_NAME] [--debug] [-v]
                       blueprint

    Generate Galaxy tool XML from blueprint JSON files with sanitizer and section
    support

    positional arguments:
      blueprint             Path to blueprint JSON file or pattern (e.g.,
                            'templates/3_galaxy-tools/*.json')

    options:
      -h, --help            show this help message and exit
      -o OUTPUT, --output OUTPUT
                            Output directory for XML files (default: galaxy_tools)
      --docker DOCKER       Docker image name (default: nciccbr/mosuite:latest)
      --citation CITATION   Citation DOI (default: 10.5281/zenodo.16371580)
      --repo-name REPO_NAME
                            Repository name used for references (default:
                            CCBR/MOSuite-Galaxy)
      --cli-command CLI_COMMAND
                            CLI command to invoke templates (default: mosuite)
      --pkg-name PKG_NAME   R package name for documentation links (default:
                            MOSuite)
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
