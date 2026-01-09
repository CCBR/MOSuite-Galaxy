# Templates

Template files for defining the Galaxy interface for MOSuite

- `0_nidap-1.0` - The original code templates from NIDAP 1.0, preserved here for posterity.
- `1_mosuite-templates` - Manually-maintained templates; these are used to automatically update the blueprints. They were originally copied and modified from the NIDAP 1.0 templates.
- `2_blueprints` - Generated from the MOSuite templates and MOSuite package code with [`write_package_json_blueprints()`](https://github.com/CCBR/MOSuite/blob/f759b46f6638bbaa3067e63ba1767e7230c81dcd/inst/extdata/galaxy/galaxy.R).
- `3_galaxy-tools` - The final XML files to define the Galaxy interface, generated with `galaxy_xml_synthesizer.py "templates/2_blueprints/*.json" --docker nciccbr/mosuite:latest --outdir templates/3_galaxy-tools`.