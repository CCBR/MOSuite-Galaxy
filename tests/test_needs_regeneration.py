"""
Unit tests for the needs_regeneration functionality.

Tests cover:
- File modification time checks
- Docker image change detection
- Script modification detection
- Blueprint modification detection
- Edge cases and error handling
"""

import pytest
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from tempfile import TemporaryDirectory
import time

from galaxysynth.galaxy_xml_synthesizer import (
    needs_regeneration,
    process_blueprint,
)


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_blueprint():
    """Sample blueprint for testing."""
    return {
        "title": "Test Tool",
        "description": "A test tool for regeneration testing",
        "r_function": "test_function",
        "inputDatasets": [],
        "parameters": [
            {
                "key": "test_param",
                "displayName": "Test Parameter",
                "paramType": "STRING",
                "defaultValue": "test",
            }
        ],
        "columns": [],
        "outputs": {"output": "output.csv"},
    }


@pytest.fixture
def sample_xml():
    """Sample XML content with docker image."""
    return """<?xml version="1.0" ?>
<tool id="mosuite_test_function" name="Test Tool" version="1.0.0" profile="24.2">
    <description>A test tool</description>
    <requirements>
        <container type="docker">nciccbr/mosuite:latest</container>
    </requirements>
    <command detect_errors="exit_code"><![CDATA[echo test]]></command>
    <inputs>
        <param name="test_param" type="text" label="Test Parameter" value="test"/>
    </inputs>
    <outputs>
        <data name="output" format="csv" from_work_dir="output.csv" label="${tool.name} on ${on_string}: output"/>
    </outputs>
    <help><![CDATA[Test help]]></help>
    <citations>
        <citation type="doi">10.5281/zenodo.16371580</citation>
    </citations>
</tool>
"""


class TestNeedsRegeneration:
    """Test suite for needs_regeneration function."""

    def test_xml_does_not_exist(self, temp_dir):
        """Test that regeneration is needed when XML doesn't exist."""
        blueprint_path = temp_dir / "blueprint.json"
        xml_path = temp_dir / "tool.xml"
        script_path = Path(__file__)

        # Create blueprint but not XML
        blueprint_path.write_text(json.dumps({"test": "data"}))

        needs_regen, reason = needs_regeneration(
            blueprint_path, xml_path, script_path, "nciccbr/mosuite:latest"
        )

        assert needs_regen is True
        assert reason == "XML file does not exist"

    def test_docker_image_changed(self, temp_dir, sample_xml):
        """Test that regeneration is needed when docker image changes."""
        blueprint_path = temp_dir / "blueprint.json"
        xml_path = temp_dir / "tool.xml"
        script_path = Path(__file__)

        # Create files
        blueprint_path.write_text(json.dumps({"test": "data"}))
        xml_path.write_text(sample_xml)

        # Wait to ensure XML is older
        time.sleep(0.01)

        # Check with different docker image
        needs_regen, reason = needs_regeneration(
            blueprint_path, xml_path, script_path, "nciccbr/mosuite:v2.0.0"
        )

        assert needs_regen is True
        assert reason == "docker image has changed"

    def test_docker_image_unchanged(self, temp_dir, sample_xml):
        """Test that regeneration is skipped when docker image is the same."""
        blueprint_path = temp_dir / "blueprint.json"
        xml_path = temp_dir / "tool.xml"
        script_path = Path(__file__)

        # Create files
        blueprint_path.write_text(json.dumps({"test": "data"}))
        xml_path.write_text(sample_xml)

        # Wait to ensure XML is older than all source files
        time.sleep(0.01)

        # Touch XML to make it newest
        xml_path.touch()
        time.sleep(0.01)

        # Check with same docker image
        needs_regen, reason = needs_regeneration(
            blueprint_path, xml_path, script_path, "nciccbr/mosuite:latest"
        )

        assert needs_regen is False
        assert reason == "up to date"

    def test_blueprint_modified(self, temp_dir, sample_xml):
        """Test that regeneration is needed when blueprint is newer than XML."""
        blueprint_path = temp_dir / "blueprint.json"
        xml_path = temp_dir / "tool.xml"
        script_path = Path(__file__)

        # Create XML first
        xml_path.write_text(sample_xml)
        time.sleep(0.01)

        # Create blueprint after XML (newer)
        blueprint_path.write_text(json.dumps({"test": "data"}))

        needs_regen, reason = needs_regeneration(
            blueprint_path, xml_path, script_path, "nciccbr/mosuite:latest"
        )

        assert needs_regen is True
        assert reason == "blueprint has been modified"

    def test_script_modified(self, temp_dir, sample_xml):
        """Test that regeneration is needed when script is newer than XML."""
        blueprint_path = temp_dir / "blueprint.json"
        xml_path = temp_dir / "tool.xml"
        script_path = temp_dir / "fake_script.py"

        # Create blueprint and XML first
        blueprint_path.write_text(json.dumps({"test": "data"}))
        xml_path.write_text(sample_xml)
        time.sleep(0.01)

        # Create script after (newer)
        script_path.write_text("# fake script")

        needs_regen, reason = needs_regeneration(
            blueprint_path, xml_path, script_path, "nciccbr/mosuite:latest"
        )

        assert needs_regen is True
        assert reason == "synthesizer script has been modified"

    def test_invalid_xml(self, temp_dir):
        """Test that regeneration is needed when XML is invalid/unreadable."""
        blueprint_path = temp_dir / "blueprint.json"
        xml_path = temp_dir / "tool.xml"
        script_path = Path(__file__)

        # Create invalid XML
        blueprint_path.write_text(json.dumps({"test": "data"}))
        xml_path.write_text("This is not valid XML!")

        needs_regen, reason = needs_regeneration(
            blueprint_path, xml_path, script_path, "nciccbr/mosuite:latest"
        )

        assert needs_regen is True
        assert reason == "XML file is invalid or unreadable"

    def test_xml_missing_container(self, temp_dir):
        """Test handling of XML missing docker container element."""
        blueprint_path = temp_dir / "blueprint.json"
        xml_path = temp_dir / "tool.xml"
        script_path = Path(__file__)

        # Create XML without container element
        invalid_xml = """<?xml version="1.0" ?>
<tool id="test" name="Test">
    <requirements>
        <!-- No container element -->
    </requirements>
</tool>
"""
        blueprint_path.write_text(json.dumps({"test": "data"}))
        xml_path.write_text(invalid_xml)

        # Should detect missing container as a change
        needs_regen, reason = needs_regeneration(
            blueprint_path, xml_path, script_path, "nciccbr/mosuite:latest"
        )

        # Since there's no container text, it won't match and should regenerate
        # or it may not find the container and skip that check
        assert needs_regen is True

    def test_all_files_up_to_date(self, temp_dir, sample_xml):
        """Test that no regeneration when all files are up to date."""
        blueprint_path = temp_dir / "blueprint.json"
        xml_path = temp_dir / "tool.xml"
        script_path = temp_dir / "script.py"

        # Create all files, then touch XML to make it newest
        blueprint_path.write_text(json.dumps({"test": "data"}))
        script_path.write_text("# script")
        time.sleep(0.01)
        xml_path.write_text(sample_xml)

        needs_regen, reason = needs_regeneration(
            blueprint_path, xml_path, script_path, "nciccbr/mosuite:latest"
        )

        assert needs_regen is False
        assert reason == "up to date"


class TestProcessBlueprintWithRegeneration:
    """Test process_blueprint with regeneration logic."""

    def test_force_flag_regenerates(self, temp_dir, sample_blueprint):
        """Test that force flag regenerates even when up to date."""
        blueprint_path = temp_dir / "blueprint.json"
        output_dir = temp_dir / "output"

        # Write blueprint
        with open(blueprint_path, "w") as f:
            json.dump(sample_blueprint, f)

        # First generation
        xml_path = process_blueprint(
            blueprint_path,
            output_dir,
            docker_image="nciccbr/mosuite:latest",
            force=False,
        )
        assert xml_path.exists()

        # Get modification time
        first_mtime = xml_path.stat().st_mtime

        # Wait a bit
        time.sleep(0.01)

        # Second run without force - should skip
        xml_path = process_blueprint(
            blueprint_path,
            output_dir,
            docker_image="nciccbr/mosuite:latest",
            force=False,
        )
        second_mtime = xml_path.stat().st_mtime
        assert second_mtime == first_mtime  # File not modified

        # Wait a bit
        time.sleep(0.01)

        # Third run with force - should regenerate
        xml_path = process_blueprint(
            blueprint_path,
            output_dir,
            docker_image="nciccbr/mosuite:latest",
            force=True,
        )
        third_mtime = xml_path.stat().st_mtime
        assert third_mtime > second_mtime  # File was modified

    def test_skip_when_up_to_date(self, temp_dir, sample_blueprint):
        """Test that processing is skipped when files are up to date."""
        blueprint_path = temp_dir / "blueprint.json"
        output_dir = temp_dir / "output"

        # Write blueprint
        with open(blueprint_path, "w") as f:
            json.dump(sample_blueprint, f)

        # First generation
        xml_path = process_blueprint(
            blueprint_path,
            output_dir,
            docker_image="nciccbr/mosuite:latest",
        )
        assert xml_path.exists()

        # Get modification time
        first_mtime = xml_path.stat().st_mtime
        time.sleep(0.01)

        # Second run - should skip
        xml_path = process_blueprint(
            blueprint_path,
            output_dir,
            docker_image="nciccbr/mosuite:latest",
        )
        second_mtime = xml_path.stat().st_mtime
        assert second_mtime == first_mtime

    def test_regenerate_on_docker_change(self, temp_dir, sample_blueprint):
        """Test that XML is regenerated when docker image changes."""
        blueprint_path = temp_dir / "blueprint.json"
        output_dir = temp_dir / "output"

        # Write blueprint
        with open(blueprint_path, "w") as f:
            json.dump(sample_blueprint, f)

        # First generation with one docker image
        xml_path = process_blueprint(
            blueprint_path,
            output_dir,
            docker_image="nciccbr/mosuite:v1.0",
        )

        # Check docker image in XML
        tree = ET.parse(xml_path)
        root = tree.getroot()
        container = root.find(".//requirements/container[@type='docker']")
        assert container.text == "nciccbr/mosuite:v1.0"

        time.sleep(0.01)

        # Second generation with different docker image
        xml_path = process_blueprint(
            blueprint_path,
            output_dir,
            docker_image="nciccbr/mosuite:v2.0",
        )

        # Check new docker image in XML
        tree = ET.parse(xml_path)
        root = tree.getroot()
        container = root.find(".//requirements/container[@type='docker']")
        assert container.text == "nciccbr/mosuite:v2.0"

    def test_regenerate_on_blueprint_change(self, temp_dir, sample_blueprint):
        """Test that XML is regenerated when blueprint changes."""
        blueprint_path = temp_dir / "blueprint.json"
        output_dir = temp_dir / "output"

        # Write blueprint
        with open(blueprint_path, "w") as f:
            json.dump(sample_blueprint, f)

        # First generation
        xml_path = process_blueprint(
            blueprint_path,
            output_dir,
            docker_image="nciccbr/mosuite:latest",
        )
        first_mtime = xml_path.stat().st_mtime

        time.sleep(0.01)

        # Modify blueprint
        sample_blueprint["description"] = "Modified description"
        with open(blueprint_path, "w") as f:
            json.dump(sample_blueprint, f)

        # Second generation - should regenerate
        xml_path = process_blueprint(
            blueprint_path,
            output_dir,
            docker_image="nciccbr/mosuite:latest",
        )
        second_mtime = xml_path.stat().st_mtime
        assert second_mtime > first_mtime


class TestDockerImageDetection:
    """Test suite for docker image detection in XML."""

    def test_extract_docker_image_from_xml(self, temp_dir, sample_xml):
        """Test extracting docker image from existing XML."""
        xml_path = temp_dir / "tool.xml"
        xml_path.write_text(sample_xml)

        # Parse and extract
        tree = ET.parse(xml_path)
        root = tree.getroot()
        container = root.find(".//requirements/container[@type='docker']")

        assert container is not None
        assert container.text == "nciccbr/mosuite:latest"

    def test_docker_image_with_different_tags(self, temp_dir):
        """Test detection with different docker image tags."""
        blueprint_path = temp_dir / "blueprint.json"
        xml_path = temp_dir / "tool.xml"
        script_path = Path(__file__)

        blueprint_path.write_text(json.dumps({"test": "data"}))

        # Test various docker images
        docker_images = [
            "nciccbr/mosuite:latest",
            "nciccbr/mosuite:v1.0.0",
            "nciccbr/mosuite:dev",
            "myrepo/myimage:tag123",
        ]

        for docker_image in docker_images:
            xml_content = f"""<?xml version="1.0" ?>
<tool id="test" name="Test">
    <requirements>
        <container type="docker">{docker_image}</container>
    </requirements>
</tool>
"""
            xml_path.write_text(xml_content)
            time.sleep(0.01)
            xml_path.touch()  # Make XML newest

            # Should not need regeneration with same image
            needs_regen, reason = needs_regeneration(
                blueprint_path, xml_path, script_path, docker_image
            )
            assert needs_regen is False

            # Should need regeneration with different image
            needs_regen, reason = needs_regeneration(
                blueprint_path, xml_path, script_path, "different/image:tag"
            )
            assert needs_regen is True
            assert reason == "docker image has changed"


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_docker_image_in_xml(self, temp_dir):
        """Test handling of empty docker image in XML."""
        blueprint_path = temp_dir / "blueprint.json"
        xml_path = temp_dir / "tool.xml"
        script_path = Path(__file__)

        blueprint_path.write_text(json.dumps({"test": "data"}))

        # XML with empty container
        xml_content = """<?xml version="1.0" ?>
<tool id="test" name="Test">
    <requirements>
        <container type="docker"></container>
    </requirements>
</tool>
"""
        xml_path.write_text(xml_content)

        needs_regen, reason = needs_regeneration(
            blueprint_path, xml_path, script_path, "nciccbr/mosuite:latest"
        )

        # Should need regeneration since XML has empty container
        assert needs_regen is True

    def test_concurrent_modifications(self, temp_dir, sample_blueprint):
        """Test behavior with concurrent file modifications."""
        blueprint_path = temp_dir / "blueprint.json"
        output_dir = temp_dir / "output"
        script_path = temp_dir / "script.py"

        # Create all files
        with open(blueprint_path, "w") as f:
            json.dump(sample_blueprint, f)
        script_path.write_text("# script")

        # Generate XML
        xml_path = process_blueprint(
            blueprint_path,
            output_dir,
            docker_image="nciccbr/mosuite:latest",
        )

        # Simulate rapid modifications
        time.sleep(0.01)
        blueprint_path.touch()  # Touch blueprint

        # Should detect change and regenerate
        xml_path = process_blueprint(
            blueprint_path,
            output_dir,
            docker_image="nciccbr/mosuite:latest",
        )
        assert xml_path.exists()

    def test_missing_requirements_section(self, temp_dir):
        """Test XML without requirements section."""
        blueprint_path = temp_dir / "blueprint.json"
        xml_path = temp_dir / "tool.xml"
        script_path = Path(__file__)

        blueprint_path.write_text(json.dumps({"test": "data"}))

        # XML without requirements
        xml_content = """<?xml version="1.0" ?>
<tool id="test" name="Test">
    <description>Test</description>
</tool>
"""
        xml_path.write_text(xml_content)

        # Should handle missing requirements gracefully
        needs_regen, reason = needs_regeneration(
            blueprint_path, xml_path, script_path, "nciccbr/mosuite:latest"
        )

        # Since container is missing, it should need regeneration
        assert needs_regen is True
