"""
Comprehensive unit tests for format_values.py.

Tests cover:
- Boolean normalization
- Repeat structure extraction
- Delimited text parsing
- Output configuration injection
- Full parameter processing
- JSON flattening
- CLI interface
- File I/O operations
- Edge cases and error handling
"""

import json
import pytest
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

# Import the format_values module
sys.path.insert(0, str(Path(__file__).parent.parent / "templates" / "3_galaxy-tools"))
from format_values import (
    normalize_boolean,
    extract_list_from_repeat,
    parse_delimited_text,
    inject_output_configuration,
    process_galaxy_params,
    flatten_json,
    main,
)


class TestNormalizeBoolean:
    """Test boolean normalization."""

    def test_true_boolean(self):
        """Test that True boolean stays True."""
        assert normalize_boolean(True) is True

    def test_false_boolean(self):
        """Test that False boolean stays False."""
        assert normalize_boolean(False) is False

    def test_true_string_variants(self):
        """Test various string representations of true."""
        assert normalize_boolean("True") is True
        assert normalize_boolean("true") is True
        assert normalize_boolean("TRUE") is True
        assert normalize_boolean("yes") is True
        assert normalize_boolean("YES") is True
        assert normalize_boolean("1") is True
        assert normalize_boolean("t") is True
        assert normalize_boolean("T") is True
        assert normalize_boolean("  true  ") is True  # with whitespace

    def test_false_string_variants(self):
        """Test various string representations of false."""
        assert normalize_boolean("False") is False
        assert normalize_boolean("false") is False
        assert normalize_boolean("FALSE") is False
        assert normalize_boolean("no") is False
        assert normalize_boolean("NO") is False
        assert normalize_boolean("0") is False
        assert normalize_boolean("f") is False
        assert normalize_boolean("F") is False
        assert normalize_boolean("none") is False
        assert normalize_boolean("None") is False
        assert normalize_boolean("") is False
        assert normalize_boolean("  ") is False  # whitespace only

    def test_none_value(self):
        """Test None is converted to False."""
        assert normalize_boolean(None) is False

    def test_numeric_values(self):
        """Test numeric values."""
        assert normalize_boolean(1) is True
        assert normalize_boolean(0) is False
        assert normalize_boolean(42) is True  # non-zero

    def test_unexpected_strings(self):
        """Test unexpected string values use bool() - non-empty strings are truthy."""
        assert normalize_boolean("maybe") is True  # Non-empty string
        assert normalize_boolean("invalid") is True  # Non-empty string


class TestExtractListFromRepeat:
    """Test list extraction from Galaxy repeat structures."""

    def test_standard_repeat_structure(self):
        """Test extraction from standard Galaxy repeat structure."""
        params = {
            "feature_repeat": [
                {"value": "CD3"},
                {"value": "CD4"},
                {"value": "CD8"},
            ]
        }
        result = extract_list_from_repeat(params, "feature")
        assert result == ["CD3", "CD4", "CD8"]

    def test_empty_repeat_structure(self):
        """Test empty repeat structure returns empty list."""
        params = {"feature_repeat": []}
        result = extract_list_from_repeat(params, "feature")
        assert result == []

    def test_repeat_with_empty_values(self):
        """Test repeat with empty values are filtered out."""
        params = {
            "feature_repeat": [
                {"value": "CD3"},
                {"value": ""},
                {"value": "  "},
                {"value": "CD4"},
            ]
        }
        result = extract_list_from_repeat(params, "feature")
        assert result == ["CD3", "CD4"]

    def test_backward_compatibility_simple_list(self):
        """Test backward compatibility with simple lists (no repeat)."""
        params = {"feature": ["CD3", "CD4", "CD8"]}
        result = extract_list_from_repeat(params, "feature")
        assert result == ["CD3", "CD4", "CD8"]

    def test_backward_compatibility_string(self):
        """Test backward compatibility with single string value."""
        params = {"feature": "CD3"}
        result = extract_list_from_repeat(params, "feature")
        assert result == ["CD3"]

    def test_backward_compatibility_empty_string(self):
        """Test backward compatibility with empty string."""
        params = {"feature": ""}
        result = extract_list_from_repeat(params, "feature")
        assert result == []

    def test_nonexistent_parameter(self):
        """Test nonexistent parameter returns empty list."""
        params = {}
        result = extract_list_from_repeat(params, "feature")
        assert result == []

    def test_whitespace_trimming(self):
        """Test that values are trimmed of whitespace."""
        params = {
            "feature_repeat": [
                {"value": "  CD3  "},
                {"value": "CD4\n"},
                {"value": "\tCD8"},
            ]
        }
        result = extract_list_from_repeat(params, "feature")
        assert result == ["CD3", "CD4", "CD8"]


class TestParseDelimitedText:
    """Test delimited text parsing."""

    def test_semicolon_separator(self):
        """Test parsing with semicolon separator."""
        text = "CD3;CD4;CD8"
        result = parse_delimited_text(text, ";")
        assert result == ["CD3", "CD4", "CD8"]

    def test_comma_separator(self):
        """Test parsing with comma separator."""
        text = "CD3,CD4,CD8"
        result = parse_delimited_text(text, ",")
        assert result == ["CD3", "CD4", "CD8"]

    def test_newline_separator(self):
        """Test parsing with newline separator."""
        text = "CD3\nCD4\nCD8"
        result = parse_delimited_text(text, "\n")
        assert result == ["CD3", "CD4", "CD8"]

    def test_newline_with_trailing_newlines(self):
        """Test parsing with trailing newlines."""
        text = "\nCD3\nCD4\nCD8\n\n"
        result = parse_delimited_text(text, "\n")
        assert result == ["CD3", "CD4", "CD8"]

    def test_whitespace_trimming(self):
        """Test that whitespace is trimmed from values."""
        text = "  CD3  ;  CD4  ;  CD8  "
        result = parse_delimited_text(text, ";")
        assert result == ["CD3", "CD4", "CD8"]

    def test_empty_values_filtered(self):
        """Test that empty values are filtered out."""
        text = "CD3;;CD4;;;CD8"
        result = parse_delimited_text(text, ";")
        assert result == ["CD3", "CD4", "CD8"]

    def test_empty_string(self):
        """Test empty string returns empty list."""
        result = parse_delimited_text("", ";")
        assert result == []

    def test_none_value(self):
        """Test None value returns empty list."""
        result = parse_delimited_text(None, ";")
        assert result == []

    def test_whitespace_only(self):
        """Test whitespace-only string returns empty list."""
        result = parse_delimited_text("   ", ";")
        assert result == []

    def test_complex_biological_notation(self):
        """Test parsing biological notation with special characters."""
        text = "CD4+; CD8+; FOXP3+/CD25+"
        result = parse_delimited_text(text, ";")
        assert result == ["CD4+", "CD8+", "FOXP3+/CD25+"]


class TestInjectOutputConfiguration:
    """Test output configuration injection."""

    def test_inject_simple_outputs(self):
        """Test injecting simple output configuration."""
        cleaned = {}
        outputs_config = {
            "output_file": {"type": "file", "name": "result.csv"},
        }
        inject_output_configuration(cleaned, outputs_config)

        assert "outputs" in cleaned
        assert cleaned["outputs"] == outputs_config
        assert cleaned["save_results"] is True

    def test_inject_multiple_outputs(self):
        """Test injecting multiple outputs."""
        cleaned = {}
        outputs_config = {
            "output_file": {"type": "file", "name": "result.csv"},
            "output_dir": {"type": "directory", "name": "figures/"},
        }
        inject_output_configuration(cleaned, outputs_config)

        assert cleaned["outputs"] == outputs_config
        assert cleaned["save_results"] is True

    def test_inject_none_config(self):
        """Test injecting None doesn't modify dict."""
        cleaned = {}
        inject_output_configuration(cleaned, None)

        assert "outputs" not in cleaned
        assert "save_results" not in cleaned

    def test_inject_empty_config(self):
        """Test injecting empty config doesn't modify dict (empty dict is falsy)."""
        cleaned = {}
        inject_output_configuration(cleaned, {})

        # Empty dict is falsy, so nothing is injected
        assert "outputs" not in cleaned
        assert "save_results" not in cleaned

    def test_inject_preserves_existing_params(self):
        """Test injection preserves existing parameters."""
        cleaned = {"param1": "value1", "param2": 42}
        outputs_config = {"output_file": {"type": "file", "name": "result.csv"}}
        inject_output_configuration(cleaned, outputs_config)

        assert cleaned["param1"] == "value1"
        assert cleaned["param2"] == 42
        assert cleaned["outputs"] == outputs_config


class TestProcessGalaxyParams:
    """Test full parameter processing."""

    def test_simple_parameter_passthrough(self):
        """Test simple parameters are passed through unchanged."""
        params = {"string_param": "value", "int_param": 42}
        result = process_galaxy_params(params, [], [])

        assert result["string_param"] == "value"
        assert result["int_param"] == 42

    def test_boolean_conversion(self):
        """Test boolean parameters are converted."""
        params = {
            "bool1": "True",
            "bool2": "false",
            "bool3": "yes",
        }
        result = process_galaxy_params(params, ["bool1", "bool2", "bool3"], [])

        assert result["bool1"] is True
        assert result["bool2"] is False
        assert result["bool3"] is True

    def test_list_extraction_from_repeat(self):
        """Test list extraction from repeat structures."""
        params = {
            "features_repeat": [
                {"value": "CD3"},
                {"value": "CD4"},
            ],
            "other_param": "value",
        }
        result = process_galaxy_params(params, [], ["features"])

        assert result["features"] == ["CD3", "CD4"]
        assert "features_repeat" not in result
        assert result["other_param"] == "value"

    def test_delimited_text_parsing(self):
        """Test delimited text parameter parsing."""
        params = {
            "anchor_list": "T cells; B cells; NK cells",
            "other_param": "value",
        }
        delimited_params = {"anchor_list": ";"}
        result = process_galaxy_params(
            params, [], ["anchor_list"], delimited_params=delimited_params
        )

        assert result["anchor_list"] == ["T cells", "B cells", "NK cells"]

    def test_newline_delimited_text(self):
        """Test newline-delimited text parsing."""
        params = {
            "text_area": "Line 1\nLine 2\nLine 3",
        }
        delimited_params = {"text_area": "\n"}
        result = process_galaxy_params(
            params, [], ["text_area"], delimited_params=delimited_params
        )

        assert result["text_area"] == ["Line 1", "Line 2", "Line 3"]

    def test_combined_processing(self):
        """Test processing with booleans, lists, and delimited params."""
        params = {
            "bool_param": "True",
            "list_repeat": [{"value": "A"}, {"value": "B"}],
            "delim_param": "X;Y;Z",
            "normal_param": "value",
        }
        delimited_params = {"delim_param": ";"}
        result = process_galaxy_params(
            params,
            ["bool_param"],
            ["list", "delim_param"],
            delimited_params=delimited_params,
        )

        assert result["bool_param"] is True
        assert result["list"] == ["A", "B"]
        assert result["delim_param"] == ["X", "Y", "Z"]
        assert result["normal_param"] == "value"
        assert "list_repeat" not in result

    def test_output_injection(self):
        """Test output injection through process_galaxy_params."""
        params = {"param": "value"}
        outputs_config = {"output": {"type": "file", "name": "out.csv"}}
        result = process_galaxy_params(
            params, [], [], outputs_config=outputs_config, inject_outputs=True
        )

        assert "outputs" in result
        assert result["outputs"] == outputs_config
        assert result["save_results"] is True

    def test_no_output_injection_by_default(self):
        """Test outputs are not injected unless requested."""
        params = {"param": "value"}
        outputs_config = {"output": {"type": "file", "name": "out.csv"}}
        result = process_galaxy_params(
            params, [], [], outputs_config=outputs_config, inject_outputs=False
        )

        assert "outputs" not in result
        assert "save_results" not in result


class TestFlattenJson:
    """Test JSON flattening."""

    def test_simple_flattening(self):
        """Test flattening simple nested structure."""
        nested = {
            "a": 1,
            "b": {"c": 2, "d": 3},
        }
        result = flatten_json(nested)

        assert result == {"a": 1, "c": 2, "d": 3}

    def test_multiple_nested_dicts(self):
        """Test flattening multiple nested dictionaries."""
        nested = {
            "a": 1,
            "b": {"c": 2},
            "d": {"e": 3, "f": 4},
        }
        result = flatten_json(nested)

        assert result == {"a": 1, "c": 2, "e": 3, "f": 4}

    def test_filter_repeat_keys(self):
        """Test that _repeat keys are filtered out."""
        nested = {
            "param": "value",
            "list_repeat": [{"value": "A"}, {"value": "B"}],
            "section": {
                "nested_param": "nested_value",
                "nested_repeat": [{"value": "X"}],
            },
        }
        result = flatten_json(nested)

        assert result == {"param": "value", "nested_param": "nested_value"}
        assert "list_repeat" not in result
        assert "nested_repeat" not in result

    def test_preserve_non_dict_values(self):
        """Test non-dict values are preserved."""
        nested = {
            "string": "text",
            "number": 42,
            "bool": True,
            "list": [1, 2, 3],
            "none": None,
        }
        result = flatten_json(nested)

        assert result["string"] == "text"
        assert result["number"] == 42
        assert result["bool"] is True
        assert result["list"] == [1, 2, 3]
        assert result["none"] is None

    def test_empty_dict(self):
        """Test empty dict returns empty dict."""
        result = flatten_json({})
        assert result == {}

    def test_already_flat(self):
        """Test already flat dict is unchanged (except _repeat filtering)."""
        flat = {"a": 1, "b": 2, "c": 3}
        result = flatten_json(flat)
        assert result == flat


class TestMainCLI:
    """Test main CLI interface."""

    def test_basic_processing(self):
        """Test basic parameter processing through CLI."""
        with TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            input_file = tmpdir / "input.json"
            output_file = tmpdir / "output.json"

            # Write input
            params = {
                "bool_param": "True",
                "string_param": "value",
            }
            with open(input_file, "w") as f:
                json.dump(params, f)

            # Run CLI
            with patch.object(
                sys,
                "argv",
                [
                    "format_values.py",
                    str(input_file),
                    str(output_file),
                    "--bool-values",
                    "bool_param",
                ],
            ):
                main()

            # Check output
            assert output_file.exists()
            with open(output_file) as f:
                result = json.load(f)

            assert result["bool_param"] is True
            assert result["string_param"] == "value"
            assert result["moo_output_rds"] == "moo.rds"

    def test_list_processing(self):
        """Test list parameter processing through CLI."""
        with TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            input_file = tmpdir / "input.json"
            output_file = tmpdir / "output.json"

            params = {
                "features_repeat": [{"value": "CD3"}, {"value": "CD4"}],
            }
            with open(input_file, "w") as f:
                json.dump(params, f)

            with patch.object(
                sys,
                "argv",
                [
                    "format_values.py",
                    str(input_file),
                    str(output_file),
                    "--list-values",
                    "features",
                ],
            ):
                main()

            with open(output_file) as f:
                result = json.load(f)

            assert result["features"] == ["CD3", "CD4"]
            assert "features_repeat" not in result

    def test_delimited_text_processing(self):
        """Test delimited text processing through CLI."""
        with TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            input_file = tmpdir / "input.json"
            output_file = tmpdir / "output.json"

            params = {
                "anchor_list": "T cells; B cells",
            }
            with open(input_file, "w") as f:
                json.dump(params, f)

            with patch.object(
                sys,
                "argv",
                [
                    "format_values.py",
                    str(input_file),
                    str(output_file),
                    "--list-sep",
                    ";",
                    "--list-fields",
                    "anchor_list",
                    "--list-values",
                    "anchor_list",
                ],
            ):
                main()

            with open(output_file) as f:
                result = json.load(f)

            assert result["anchor_list"] == ["T cells", "B cells"]

    def test_newline_separator(self):
        """Test newline separator through CLI."""
        with TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            input_file = tmpdir / "input.json"
            output_file = tmpdir / "output.json"

            params = {
                "text_area": "Line 1\nLine 2\nLine 3",
            }
            with open(input_file, "w") as f:
                json.dump(params, f)

            with patch.object(
                sys,
                "argv",
                [
                    "format_values.py",
                    str(input_file),
                    str(output_file),
                    "--list-sep",
                    "\\n",  # Escaped newline
                    "--list-fields",
                    "text_area",
                    "--list-values",
                    "text_area",
                ],
            ):
                main()

            with open(output_file) as f:
                result = json.load(f)

            assert result["text_area"] == ["Line 1", "Line 2", "Line 3"]

    def test_empty_value_removal(self):
        """Test that empty lists, strings, and None are removed."""
        with TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            input_file = tmpdir / "input.json"
            output_file = tmpdir / "output.json"

            params = {
                "empty_list": [],
                "empty_string": "",
                "whitespace_string": "   ",
                "null_value": None,
                "valid_value": "keep_me",
            }
            with open(input_file, "w") as f:
                json.dump(params, f)

            with patch.object(
                sys, "argv", ["format_values.py", str(input_file), str(output_file)]
            ):
                main()

            with open(output_file) as f:
                result = json.load(f)

            assert "empty_list" not in result
            assert "empty_string" not in result
            assert "whitespace_string" not in result
            assert "null_value" not in result
            assert result["valid_value"] == "keep_me"

    def test_missing_input_file(self):
        """Test error handling for missing input file."""
        with TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            input_file = tmpdir / "nonexistent.json"
            output_file = tmpdir / "output.json"

            with patch.object(
                sys, "argv", ["format_values.py", str(input_file), str(output_file)]
            ):
                with pytest.raises(SystemExit) as exc_info:
                    main()

                assert exc_info.value.code == 1

    def test_invalid_json_input(self):
        """Test error handling for invalid JSON."""
        with TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            input_file = tmpdir / "invalid.json"
            output_file = tmpdir / "output.json"

            # Write invalid JSON
            with open(input_file, "w") as f:
                f.write("{ invalid json }")

            with patch.object(
                sys, "argv", ["format_values.py", str(input_file), str(output_file)]
            ):
                with pytest.raises(SystemExit) as exc_info:
                    main()

                assert exc_info.value.code == 1

    def test_nested_params_flattening(self):
        """Test that nested parameters are flattened."""
        with TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            input_file = tmpdir / "input.json"
            output_file = tmpdir / "output.json"

            params = {
                "top_level": "value1",
                "section": {
                    "nested_param": "value2",
                    "another_nested": "value3",
                },
            }
            with open(input_file, "w") as f:
                json.dump(params, f)

            with patch.object(
                sys, "argv", ["format_values.py", str(input_file), str(output_file)]
            ):
                main()

            with open(output_file) as f:
                result = json.load(f)

            assert result["top_level"] == "value1"
            assert result["nested_param"] == "value2"
            assert result["another_nested"] == "value3"
            assert "section" not in result


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_numeric_string_values_in_list(self):
        """Test numeric values in lists are converted to strings."""
        params = {
            "values_repeat": [
                {"value": 1},
                {"value": 2},
                {"value": 3},
            ]
        }
        result = extract_list_from_repeat(params, "values")
        assert result == ["1", "2", "3"]

    def test_mixed_type_list(self):
        """Test mixed type values in repeat structure."""
        params = {
            "mixed_repeat": [
                {"value": "string"},
                {"value": 42},
                {"value": True},
            ]
        }
        result = extract_list_from_repeat(params, "mixed")
        assert result == ["string", "42", "True"]

    def test_unicode_text_parsing(self):
        """Test parsing text with unicode characters."""
        text = "α; β; γ; δ"
        result = parse_delimited_text(text, ";")
        assert result == ["α", "β", "γ", "δ"]

    def test_special_characters_in_values(self):
        """Test values with special characters are preserved."""
        params = {
            "special_repeat": [
                {"value": "CD4+"},
                {"value": "FOXP3+/CD25+"},
                {"value": "PD-1<high>"},
            ]
        }
        result = extract_list_from_repeat(params, "special")
        assert result == ["CD4+", "FOXP3+/CD25+", "PD-1<high>"]

    def test_very_long_list(self):
        """Test processing very long lists."""
        params = {"long_repeat": [{"value": f"item_{i}"} for i in range(1000)]}
        result = extract_list_from_repeat(params, "long")
        assert len(result) == 1000
        assert result[0] == "item_0"
        assert result[-1] == "item_999"

    def test_deeply_nested_json(self):
        """Test flattening deeply nested JSON."""
        nested = {
            "level1": {
                "level2": {
                    "level3": "value",
                }
            }
        }
        # Only flattens one level
        result = flatten_json(nested)
        assert "level2" in result
        assert result["level2"] == {"level3": "value"}

    def test_parameter_with_repeat_in_name(self):
        """Test parameter with '_repeat' substring is filtered by flatten_json."""
        params = {
            "count": 5,
            "do_something": True,
            "my_repeat_param": 99,  # Will be filtered - contains '_repeat'
            "repeat_count": 7,  # Will NOT be filtered - doesn't contain '_repeat'
        }
        result = flatten_json(params)
        assert result["count"] == 5
        assert result["do_something"] is True
        assert result["repeat_count"] == 7  # Preserved
        assert "my_repeat_param" not in result  # Filtered because it contains '_repeat'

    def test_case_sensitivity(self):
        """Test that parameter names are case-sensitive."""
        params = {
            "Param": "upper",
            "param": "lower",
            "PARAM": "all_upper",
        }
        result = process_galaxy_params(params, [], [])
        assert result["Param"] == "upper"
        assert result["param"] == "lower"
        assert result["PARAM"] == "all_upper"
