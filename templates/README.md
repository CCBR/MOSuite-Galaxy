# Templates

Template files for defining the Galaxy interface for MOSuite

- `0_nidap-1.0` - the original code templates from NIDAP 1.0, preserved here for posterity.
- `1_mosuite-templates` - originally copied and modified from the NIDAP 1.0 templates. These templates are used by MOSuite to create the blueprints.
- `2_blueprints` - generated from the MOSuite templates with [`write_package_json_blueprints()`](https://github.com/CCBR/MOSuite/blob/f759b46f6638bbaa3067e63ba1767e7230c81dcd/inst/extdata/galaxy/galaxy.R).
- `3_galaxy-tools` - the final XML files to define the Galaxy interface, generated with `galaxy_xml_synthesizer.py "templates/2_blueprints/*.json" --docker nciccbr/mosuite:latest --outdir templates/3_galaxy-tools`.