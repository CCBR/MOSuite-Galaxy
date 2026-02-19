"""
Comprehensive unit tests for GalaxyXMLSynthesizer.

Tests cover:
- Class initialization with various configurations
- XML generation for different parameter types
- Section grouping and ordering
- Sanitizer configuration
- Command generation
- Output handling
- Helper methods
- Edge cases
"""

import pytest
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from tempfile import TemporaryDirectory

from galaxysynth.galaxy_xml_synthesizer import (
    GalaxyXMLSynthesizer,
    process_blueprint,
    batch_process,
)


# Sample blueprint fixtures
@pytest.fixture
def minimal_blueprint():
    """Minimal valid blueprint for testing."""
    return {
        "title": "Test Tool",
        "description": "A test tool for unit testing",
        "r_function": "test_function",
        "inputDatasets": [],
        "parameters": [],
        "columns": [],
        "outputs": {},
    }


@pytest.fixture
def comprehensive_blueprint():
    """Comprehensive blueprint with various parameter types."""
    return {
        "title": "Comprehensive Test Tool",
        "description": "A comprehensive test tool with all parameter types",
        "r_function": "comprehensive_test",
        "inputDatasets": [
            {
                "key": "input_file",
                "displayName": "Input File",
                "paramType": "TABULAR",
                "description": "Input data file",
            },
        ],
        "parameters": [
            {
                "key": "string_param",
                "displayName": "String Parameter",
                "paramType": "STRING",
                "defaultValue": "default",
                "description": "A string parameter",
            },
            {
                "key": "bool_param",
                "displayName": "Boolean Parameter",
                "paramType": "BOOLEAN",
                "defaultValue": True,
                "description": "A boolean parameter",
            },
            {
                "key": "int_param",
                "displayName": "Integer Parameter",
                "paramType": "INTEGER",
                "defaultValue": 10,
                "paramMin": 1,
                "paramMax": 100,
                "description": "An integer parameter",
            },
            {
                "key": "float_param",
                "displayName": "Float Parameter",
                "paramType": "FLOAT",
                "defaultValue": 0.5,
                "paramMin": 0.0,
                "paramMax": 1.0,
                "description": "A float parameter",
            },
            {
                "key": "select_param",
                "displayName": "Select Parameter",
                "paramType": "SELECT",
                "defaultValue": "option1",
                "paramValues": ["option1", "option2", "option3"],
                "description": "A select parameter",
            },
            {
                "key": "list_param",
                "displayName": "List Parameter",
                "paramType": "LIST",
                "defaultValue": ["item1", "item2"],
                "description": "A list parameter",
            },
        ],
        "columns": [
            {
                "key": "single_column",
                "displayName": "Single Column",
                "description": "A single value column",
                "isMulti": False,
                "defaultValue": "value",
            },
            {
                "key": "multi_column",
                "displayName": "Multi Column",
                "description": "A multi-value column",
                "isMulti": True,
                "defaultValue": ["val1", "val2"],
            },
        ],
        "outputs": {
            "output_file": {"type": "file", "name": "output.csv"},
            "output_dir": {"type": "directory", "name": "results/"},
        },
    }


@pytest.fixture
def sectioned_blueprint():
    """Blueprint with parameter grouping."""
    return {
        "title": "Sectioned Tool",
        "description": "Tool with parameter sections",
        "r_function": "sectioned_test",
        "inputDatasets": [
            {
                "key": "input_data",
                "displayName": "Input Data",
                "paramType": "TABULAR",
            }
        ],
        "parameters": [
            {
                "key": "ungrouped_param",
                "displayName": "Ungrouped",
                "paramType": "STRING",
                "defaultValue": "test",
            },
            {
                "key": "basic_param",
                "displayName": "Basic Parameter",
                "paramType": "STRING",
                "paramGroup": "Basic",
                "defaultValue": "basic",
            },
            {
                "key": "advanced_param",
                "displayName": "Advanced Parameter",
                "paramType": "INTEGER",
                "paramGroup": "Advanced",
                "defaultValue": 5,
            },
        ],
        "orderedMustacheKeys": [
            "input_data",
            "ungrouped_param",
            "basic_param",
            "advanced_param",
        ],
        "outputs": {"result": {"type": "file", "name": "result.txt"}},
    }


class TestGalaxyXMLSynthesizerInit:
    """Test initialization of GalaxyXMLSynthesizer."""

    def test_init_with_defaults(self, minimal_blueprint):
        """Test initialization with default parameters."""
        synth = GalaxyXMLSynthesizer(minimal_blueprint)
        assert synth.blueprint == minimal_blueprint
        assert synth.docker_image == "nciccbr/mosuite:latest"
        assert synth.citation_doi == "10.5281/zenodo.16371580"
        assert synth.repo_name == "CCBR/MOSuite-Galaxy"
        assert synth.cli_command == "mosuite"
        assert synth.pkg_name == "MOSuite"

    def test_init_with_custom_values(self, minimal_blueprint):
        """Test initialization with custom parameters."""
        synth = GalaxyXMLSynthesizer(
            minimal_blueprint,
            docker_image="custom/image:v1.0",
            citation_doi="10.1234/custom.doi",
            repo_name="custom/repo",
            cli_command="customcli",
            pkg_name="CustomPkg",
        )
        assert synth.docker_image == "custom/image:v1.0"
        assert synth.citation_doi == "10.1234/custom.doi"
        assert synth.repo_name == "custom/repo"
        assert synth.cli_command == "customcli"
        assert synth.pkg_name == "CustomPkg"


class TestXMLGeneration:
    """Test XML generation and structure."""

    def test_synthesize_creates_valid_xml(self, minimal_blueprint):
        """Test that synthesize() creates valid XML."""
        synth = GalaxyXMLSynthesizer(minimal_blueprint)
        xml_str = synth.synthesize()

        # Parse to verify valid XML
        root = ET.fromstring(xml_str)
        assert root.tag == "tool"

    def test_tool_attributes(self, minimal_blueprint):
        """Test tool element has correct attributes."""
        synth = GalaxyXMLSynthesizer(minimal_blueprint)
        xml_str = synth.synthesize()
        root = ET.fromstring(xml_str)

        assert "id" in root.attrib
        assert root.attrib["name"] == "Test Tool"
        assert "version" in root.attrib
        assert root.attrib["profile"] == "24.2"

    def test_xml_element_order(self, minimal_blueprint):
        """Test that XML elements are in correct order."""
        synth = GalaxyXMLSynthesizer(minimal_blueprint)
        xml_str = synth.synthesize()
        root = ET.fromstring(xml_str)

        expected_order = [
            "description",
            "requirements",
            "command",
            "configfiles",
            "inputs",
            "outputs",
            "help",
            "citations",
        ]

        actual_order = [child.tag for child in root]
        assert actual_order == expected_order

    def test_command_before_configfiles(self, minimal_blueprint):
        """Test that command comes before configfiles (Galaxy best practice)."""
        synth = GalaxyXMLSynthesizer(minimal_blueprint)
        xml_str = synth.synthesize()
        root = ET.fromstring(xml_str)

        tags = [child.tag for child in root]
        command_idx = tags.index("command")
        configfiles_idx = tags.index("configfiles")

        assert command_idx < configfiles_idx


class TestParameterHandling:
    """Test handling of different parameter types."""

    def test_string_parameter(self, comprehensive_blueprint):
        """Test STRING parameter generation."""
        synth = GalaxyXMLSynthesizer(comprehensive_blueprint)
        xml_str = synth.synthesize()
        root = ET.fromstring(xml_str)

        inputs = root.find("inputs")
        string_param = inputs.find(".//param[@name='string_param']")

        assert string_param is not None
        assert string_param.attrib["type"] == "text"
        assert string_param.attrib["label"] == "String Parameter"
        assert string_param.attrib["value"] == "default"

    def test_boolean_parameter(self, comprehensive_blueprint):
        """Test BOOLEAN parameter generation."""
        synth = GalaxyXMLSynthesizer(comprehensive_blueprint)
        xml_str = synth.synthesize()
        root = ET.fromstring(xml_str)

        inputs = root.find("inputs")
        bool_param = inputs.find(".//param[@name='bool_param']")

        assert bool_param is not None
        assert bool_param.attrib["type"] == "boolean"
        assert bool_param.attrib["checked"] == "true"
        assert bool_param.attrib["truevalue"] == "True"
        assert bool_param.attrib["falsevalue"] == "False"

    def test_integer_parameter_with_bounds(self, comprehensive_blueprint):
        """Test INTEGER parameter with min/max bounds."""
        synth = GalaxyXMLSynthesizer(comprehensive_blueprint)
        xml_str = synth.synthesize()
        root = ET.fromstring(xml_str)

        inputs = root.find("inputs")
        int_param = inputs.find(".//param[@name='int_param']")

        assert int_param is not None
        assert int_param.attrib["type"] == "integer"
        assert int_param.attrib["value"] == "10"
        assert int_param.attrib["min"] == "1"
        assert int_param.attrib["max"] == "100"

    def test_float_parameter(self, comprehensive_blueprint):
        """Test FLOAT parameter generation."""
        synth = GalaxyXMLSynthesizer(comprehensive_blueprint)
        xml_str = synth.synthesize()
        root = ET.fromstring(xml_str)

        inputs = root.find("inputs")
        float_param = inputs.find(".//param[@name='float_param']")

        assert float_param is not None
        assert float_param.attrib["type"] == "float"
        assert float_param.attrib["value"] == "0.5"
        assert float_param.attrib["min"] == "0.0"
        assert float_param.attrib["max"] == "1.0"

    def test_select_parameter(self, comprehensive_blueprint):
        """Test SELECT parameter with options."""
        synth = GalaxyXMLSynthesizer(comprehensive_blueprint)
        xml_str = synth.synthesize()
        root = ET.fromstring(xml_str)

        inputs = root.find("inputs")
        select_param = inputs.find(".//param[@name='select_param']")

        assert select_param is not None
        assert select_param.attrib["type"] == "select"

        options = select_param.findall("option")
        assert len(options) == 3
        assert options[0].attrib["value"] == "option1"
        assert options[0].attrib["selected"] == "true"

    def test_list_parameter_as_repeat(self, comprehensive_blueprint):
        """Test LIST parameter generates repeat structure."""
        synth = GalaxyXMLSynthesizer(comprehensive_blueprint)
        xml_str = synth.synthesize()
        root = ET.fromstring(xml_str)

        inputs = root.find("inputs")
        repeat = inputs.find(".//repeat[@name='list_param_repeat']")

        assert repeat is not None
        assert repeat.attrib["title"] == "List Parameter"

        param = repeat.find("param[@name='value']")
        assert param is not None
        assert param.attrib["type"] == "text"

    def test_dataset_parameter(self, comprehensive_blueprint):
        """Test input dataset parameter."""
        synth = GalaxyXMLSynthesizer(comprehensive_blueprint)
        xml_str = synth.synthesize()
        root = ET.fromstring(xml_str)

        inputs = root.find("inputs")
        dataset_param = inputs.find(".//param[@name='input_file']")

        assert dataset_param is not None
        assert dataset_param.attrib["type"] == "data"
        assert "tabular" in dataset_param.attrib["format"]


class TestSectionGrouping:
    """Test parameter section grouping."""

    def test_sections_created(self, sectioned_blueprint):
        """Test that sections are created for grouped parameters."""
        synth = GalaxyXMLSynthesizer(sectioned_blueprint)
        xml_str = synth.synthesize()
        root = ET.fromstring(xml_str)

        inputs = root.find("inputs")
        sections = inputs.findall("section")

        assert len(sections) == 2  # Basic and Advanced

    def test_ungrouped_before_sections(self, sectioned_blueprint):
        """Test ungrouped parameters appear before sections."""
        synth = GalaxyXMLSynthesizer(sectioned_blueprint)
        xml_str = synth.synthesize()
        root = ET.fromstring(xml_str)

        inputs = root.find("inputs")
        children = list(inputs)

        # Find ungrouped param and first section
        ungrouped_idx = next(
            i
            for i, child in enumerate(children)
            if child.tag == "param" and child.attrib.get("name") == "ungrouped_param"
        )
        first_section_idx = next(
            i for i, child in enumerate(children) if child.tag == "section"
        )

        assert ungrouped_idx < first_section_idx

    def test_section_ids_valid(self, sectioned_blueprint):
        """Test section IDs are valid (lowercase, underscores)."""
        synth = GalaxyXMLSynthesizer(sectioned_blueprint)
        xml_str = synth.synthesize()
        root = ET.fromstring(xml_str)

        inputs = root.find("inputs")
        sections = inputs.findall("section")

        for section in sections:
            section_id = section.attrib["name"]
            assert section_id.islower() or "_" in section_id
            assert section_id.isidentifier()  # Valid Python identifier


class TestOutputHandling:
    """Test output generation."""

    def test_file_output(self, comprehensive_blueprint):
        """Test file output generation."""
        synth = GalaxyXMLSynthesizer(comprehensive_blueprint)
        xml_str = synth.synthesize()
        root = ET.fromstring(xml_str)

        outputs = root.find("outputs")
        file_output = outputs.find(".//data[@name='output_file']")

        assert file_output is not None
        assert file_output.attrib["format"] == "csv"
        assert file_output.attrib["from_work_dir"] == "output.csv"

    def test_directory_output_as_collection(self, comprehensive_blueprint):
        """Test directory output generates collection."""
        synth = GalaxyXMLSynthesizer(comprehensive_blueprint)
        xml_str = synth.synthesize()
        root = ET.fromstring(xml_str)

        outputs = root.find("outputs")
        collection = outputs.find(".//collection[@name='output_dir']")

        assert collection is not None
        assert collection.attrib["type"] == "list"

        discover = collection.find("discover_datasets")
        assert discover is not None
        assert discover.attrib["directory"] == "results/"

    def test_debug_outputs_included(self, minimal_blueprint):
        """Test debug JSON outputs are always included."""
        synth = GalaxyXMLSynthesizer(minimal_blueprint)
        xml_str = synth.synthesize()
        root = ET.fromstring(xml_str)

        outputs = root.find("outputs")
        debug_outputs = [
            data
            for data in outputs.findall("data")
            if "debug" in data.attrib.get("name", "")
        ]

        assert len(debug_outputs) == 2  # params_json_debug and cleaned_params_debug


class TestCommandGeneration:
    """Test command section generation."""

    def test_command_contains_cli_command(self, minimal_blueprint):
        """Test command uses configured CLI command."""
        synth = GalaxyXMLSynthesizer(minimal_blueprint, cli_command="customcli")
        xml_str = synth.synthesize()
        root = ET.fromstring(xml_str)

        command = root.find("command")
        assert "customcli" in command.text

    def test_command_has_format_values_script(self, comprehensive_blueprint):
        """Test command includes format_values.py."""
        synth = GalaxyXMLSynthesizer(comprehensive_blueprint)
        xml_str = synth.synthesize()
        root = ET.fromstring(xml_str)

        command = root.find("command")
        assert "format_values.py" in command.text

    def test_command_includes_bool_params(self, comprehensive_blueprint):
        """Test command includes --bool-values for boolean parameters."""
        synth = GalaxyXMLSynthesizer(comprehensive_blueprint)
        xml_str = synth.synthesize()
        root = ET.fromstring(xml_str)

        command = root.find("command")
        assert "--bool-values" in command.text
        assert "bool_param" in command.text

    def test_command_includes_list_params(self, comprehensive_blueprint):
        """Test command includes --list-values for list parameters."""
        synth = GalaxyXMLSynthesizer(comprehensive_blueprint)
        xml_str = synth.synthesize()
        root = ET.fromstring(xml_str)

        command = root.find("command")
        assert "--list-values" in command.text
        assert "list_param" in command.text


class TestHelperMethods:
    """Test helper methods."""

    def test_make_tool_id(self):
        """Test tool ID generation."""
        synth = GalaxyXMLSynthesizer({"r_function": "test_function"})
        tool_id = synth._make_tool_id("test_function")

        assert tool_id == "mosuite_test_function"
        assert tool_id.islower()

    def test_make_tool_id_with_custom_prefix(self):
        """Test tool ID with custom CLI command."""
        synth = GalaxyXMLSynthesizer({"r_function": "test"}, cli_command="custom")
        tool_id = synth._make_tool_id("test")

        assert tool_id == "custom_test"

    def test_clean_text_removes_markdown(self):
        """Test markdown removal from text."""
        synth = GalaxyXMLSynthesizer({})
        text = "This is [a link](http://example.com) in text"
        cleaned = synth._clean_text(text)

        assert "a link" in cleaned
        assert "http://example.com" not in cleaned

    def test_extract_docker_tag(self):
        """Test Docker tag extraction."""
        synth = GalaxyXMLSynthesizer({})

        assert synth._extract_docker_tag("repo/image:v1.0") == "v1.0"
        assert synth._extract_docker_tag("repo/image:latest") == "latest"
        assert synth._extract_docker_tag("repo/image") == "latest"

    def test_make_section_id(self):
        """Test section ID generation."""
        synth = GalaxyXMLSynthesizer({})

        assert synth._make_section_id("Basic Parameters") == "basic_parameters"
        assert synth._make_section_id("Advanced Settings") == "advanced_settings"
        assert synth._make_section_id("Special-Chars!") == "specialchars"

    def test_get_galaxy_param_type(self):
        """Test parameter type mapping."""
        synth = GalaxyXMLSynthesizer({})

        assert synth._get_galaxy_param_type("STRING") == "text"
        assert synth._get_galaxy_param_type("INTEGER") == "integer"
        assert synth._get_galaxy_param_type("FLOAT") == "float"
        assert synth._get_galaxy_param_type("BOOLEAN") == "boolean"
        assert synth._get_galaxy_param_type("SELECT") == "select"


class TestSanitizerSupport:
    """Test sanitizer configuration."""

    def test_sanitizer_for_special_params(self):
        """Test sanitizer added for parameters needing special characters."""
        blueprint = {
            "title": "Test",
            "r_function": "test",
            "parameters": [
                {
                    "key": "Anchor_Neighbor_List",
                    "displayName": "Anchor Neighbor List",
                    "paramType": "STRING",
                    "description": "List with semicolons",
                }
            ],
            "outputs": {},
        }

        synth = GalaxyXMLSynthesizer(blueprint)
        xml_str = synth.synthesize()
        root = ET.fromstring(xml_str)

        inputs = root.find("inputs")
        param = inputs.find(".//param[@name='Anchor_Neighbor_List']")
        sanitizer = param.find("sanitizer")

        assert sanitizer is not None

    def test_sanitizer_allowed_chars(self):
        """Test sanitizer includes allowed special characters."""
        blueprint = {
            "title": "Test",
            "r_function": "test",
            "parameters": [
                {
                    "key": "Anchor_Neighbor_List",
                    "displayName": "List",
                    "paramType": "STRING",
                }
            ],
            "outputs": {},
        }

        synth = GalaxyXMLSynthesizer(blueprint)
        xml_str = synth.synthesize()
        root = ET.fromstring(xml_str)

        inputs = root.find("inputs")
        param = inputs.find(".//param[@name='Anchor_Neighbor_List']")
        sanitizer = param.find("sanitizer")
        valid = sanitizer.find("valid")
        adds = valid.findall("add")

        # Check some expected special characters are allowed
        values = [add.attrib["value"] for add in adds]
        assert ";" in values
        assert "+" in values


class TestProcessBlueprint:
    """Test process_blueprint function."""

    def test_process_blueprint_creates_xml_file(self, minimal_blueprint):
        """Test that process_blueprint creates an XML file."""
        with TemporaryDirectory() as tmpdir:
            blueprint_path = Path(tmpdir) / "test.json"
            output_dir = Path(tmpdir) / "output"

            # Write blueprint
            with open(blueprint_path, "w") as f:
                json.dump(minimal_blueprint, f)

            # Process
            xml_path = process_blueprint(blueprint_path, output_dir)

            assert xml_path.exists()
            assert xml_path.suffix == ".xml"

    def test_process_blueprint_with_custom_params(self, minimal_blueprint):
        """Test process_blueprint with custom parameters."""
        with TemporaryDirectory() as tmpdir:
            blueprint_path = Path(tmpdir) / "test.json"
            output_dir = Path(tmpdir) / "output"

            with open(blueprint_path, "w") as f:
                json.dump(minimal_blueprint, f)

            xml_path = process_blueprint(
                blueprint_path,
                output_dir,
                docker_image="custom:v1",
                citation_doi="10.1234/test",
                repo_name="test/repo",
                cli_command="testcli",
                pkg_name="TestPkg",
            )

            # Verify custom values in XML
            with open(xml_path) as f:
                content = f.read()
                assert "custom:v1" in content
                assert "10.1234/test" in content
                assert "testcli" in content


class TestBatchProcess:
    """Test batch_process function."""

    def test_batch_process_multiple_files(self, minimal_blueprint):
        """Test batch processing multiple blueprint files."""
        with TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            blueprints_dir = tmpdir / "blueprints"
            blueprints_dir.mkdir()

            # Create multiple blueprint files
            for i in range(3):
                blueprint = minimal_blueprint.copy()
                blueprint["title"] = f"Test Tool {i}"
                blueprint["r_function"] = f"test_function_{i}"

                blueprint_path = blueprints_dir / f"blueprint_{i}.json"
                with open(blueprint_path, "w") as f:
                    json.dump(blueprint, f)

            output_dir = tmpdir / "output"

            # Process
            result = batch_process(
                str(blueprints_dir / "*.json"),
                str(output_dir),
            )

            assert result == 0
            xml_files = list(output_dir.glob("*.xml"))
            assert len(xml_files) == 3

    def test_batch_process_handles_errors(self):
        """Test batch_process handles invalid blueprints gracefully."""
        with TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            blueprints_dir = tmpdir / "blueprints"
            blueprints_dir.mkdir()

            # Create invalid blueprint
            invalid_blueprint = {"invalid": "data"}
            blueprint_path = blueprints_dir / "invalid.json"
            with open(blueprint_path, "w") as f:
                json.dump(invalid_blueprint, f)

            output_dir = tmpdir / "output"

            # Should not crash
            batch_process(
                str(blueprints_dir / "*.json"),
                str(output_dir),
            )

            # Invalid blueprint might produce an XML anyway, just check it doesn't crash


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_blueprint(self):
        """Test handling of minimal/empty blueprint."""
        blueprint = {}
        synth = GalaxyXMLSynthesizer(blueprint)
        xml_str = synth.synthesize()

        # Should still produce valid XML
        root = ET.fromstring(xml_str)
        assert root.tag == "tool"

    def test_optional_parameters(self):
        """Test optional parameters are handled correctly."""
        blueprint = {
            "title": "Test",
            "r_function": "test",
            "parameters": [
                {
                    "key": "optional_param",
                    "displayName": "Optional",
                    "paramType": "STRING",
                    "optional": True,
                }
            ],
            "outputs": {},
        }

        synth = GalaxyXMLSynthesizer(blueprint)
        xml_str = synth.synthesize()
        root = ET.fromstring(xml_str)

        inputs = root.find("inputs")
        param = inputs.find(".//param[@name='optional_param']")

        assert param.attrib.get("optional") == "true"

    def test_parameter_without_default(self):
        """Test parameters without default values."""
        blueprint = {
            "title": "Test",
            "r_function": "test",
            "parameters": [
                {
                    "key": "no_default",
                    "displayName": "No Default",
                    "paramType": "STRING",
                }
            ],
            "outputs": {},
        }

        synth = GalaxyXMLSynthesizer(blueprint)
        xml_str = synth.synthesize()
        root = ET.fromstring(xml_str)

        inputs = root.find("inputs")
        param = inputs.find(".//param[@name='no_default']")

        # Should have empty default for non-optional string
        assert param.attrib.get("value") == ""

    def test_multiselect_parameter(self):
        """Test MULTISELECT parameter type."""
        blueprint = {
            "title": "Test",
            "r_function": "test",
            "parameters": [
                {
                    "key": "multi_select",
                    "displayName": "Multi Select",
                    "paramType": "MULTISELECT",
                    "paramValues": ["opt1", "opt2", "opt3"],
                }
            ],
            "outputs": {},
        }

        synth = GalaxyXMLSynthesizer(blueprint)
        xml_str = synth.synthesize()
        root = ET.fromstring(xml_str)

        inputs = root.find("inputs")
        param = inputs.find(".//param[@name='multi_select']")

        assert param.attrib["type"] == "select"
        assert param.attrib.get("multiple") == "true"
        assert param.attrib.get("optional") == "true"

    def test_positive_integer_parameter(self):
        """Test 'Positive integer' parameter type."""
        blueprint = {
            "title": "Test",
            "r_function": "test",
            "parameters": [
                {
                    "key": "pos_int",
                    "displayName": "Positive Integer",
                    "paramType": "Positive integer",
                    "defaultValue": 5,
                }
            ],
            "outputs": {},
        }

        synth = GalaxyXMLSynthesizer(blueprint)
        xml_str = synth.synthesize()
        root = ET.fromstring(xml_str)

        inputs = root.find("inputs")
        param = inputs.find(".//param[@name='pos_int']")

        assert param.attrib["type"] == "integer"
        assert param.attrib.get("min") == "1"
