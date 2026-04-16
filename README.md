# MOSuite-Galaxy

<!-- README.md is generated from README.qmd. Please edit that file -->

Galaxy workflow for [MOSuite](https://github.com/CCBR/MOSuite)

[![](https://github.com/CCBR/MOSuite-Galaxy/actions/workflows/build.yml/badge.svg)](https://github.com/CCBR/MOSuite-Galaxy/actions/workflows/build.yml)
[![codecov](https://codecov.io/gh/CCBR/MOSuite-Galaxy/graph/badge.svg?token=QV46CjB0Bg)](https://codecov.io/gh/CCBR/MOSuite-Galaxy)

- [▶️ MOSuite Workflow on
  Galaxy](http://k8s-galaxy-ffd82cb77f-464836041.us-east-1.elb.amazonaws.com/u/kelly-sovacool/w/mosuite)
- [🧬 NIDAP training dataset on
  Galaxy](http://k8s-galaxy-ffd82cb77f-464836041.us-east-1.elb.amazonaws.com/u/kelly-sovacool/h/nidap-bulk-rna-seq-training-dataset)

## Help & Contributing

Come across a **bug**? Open an
[issue](https://github.com/CCBR/MOSuite-Galaxy/issues) and include a
minimal reproducible example.

Have a **question**? Ask it in
[discussions](https://github.com/CCBR/MOSuite-Galaxy/discussions).

Want to **contribute** to this project? Check out the [contributing
guidelines](https://CCBR.github.io/MOSuite-Galaxy/CONTRIBUTING).

## Updating the Galaxy XML files for MOSuite

### Installation

```bash
pip install git+https://github.com/CCBR/MOSuite-Galaxy
```

### Usage

```bash
galaxysynth --help
```

    usage: galaxysynth [-h] [-o OUTPUT] [--docker DOCKER] [--citation CITATION]
                       [--repo-name REPO_NAME] [--cli-command CLI_COMMAND]
                       [--pkg-name PKG_NAME] [--debug] [-f] [-v]
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
      -f, --force           Force regeneration even if files are up to date
      -v, --version         show program's version number and exit

```bash
galaxysynth  "templates/2_blueprints/*.json" \
    --docker nciccbr/mosuite:v0.3.0 \
    --output templates/3_galaxy-tools
```

### Developer notes

- Please view the [contributing guide](.github/CONTRIBUTING.md) before
  opening a pull request.
- Galaxy Tool XML documentation:
  <https://docs.galaxyproject.org/en/master/dev/schema.html>
