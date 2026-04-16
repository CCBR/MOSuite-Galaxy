"""
Utility functions for the package
"""

import re
import pathlib


def repo_base(*paths):
    """
    Get the absolute path to a file in the repository

    Args:
        *paths (str): Additional paths to join with the base path.

    Returns:
        path (str): The absolute path to the file in the repository.
    """
    basedir = pathlib.Path(__file__).absolute().parent
    return basedir.joinpath(*paths)


def get_version():
    """
    Get the version of the package from the VERSION file

    Returns:
        version (str): The version of the package.
    """
    version_file = repo_base("VERSION")
    with open(version_file, "r") as vf:
        version = vf.read().strip()
    return version


def match_semver(version_str, with_leading_v=False, strict_semver=True, pattern=None):
    """
    Match a version string against the semantic versioning pattern.

    Adapted from CCBR/Tools:
    <https://github.com/CCBR/Tools/blob/51b3aebb4d02019f1f5967540ddb86129fd4e4df/src/ccbr_tools/versions.py>

    See the semantic versioning guidelines: <https://semver.org/>

    Args:
        version_str (str): The version string to match against the semantic versioning pattern.
        with_leading_v (bool): If True, the version string is expected to start with a leading 'v'.
        strict_semver (bool): If True, the version string must match the full semantic versioning pattern. Otherwise, a relaxed format with only the major and minor components is allowed.
        pattern (str, optional): A custom regex pattern to match against the version string. If None, the default semantic versioning pattern is used.
    Returns:
        re.Match or None
            The match object if the version string matches the semantic versioning pattern, otherwise None.

    Examples:
        >>> match_semver("1.0.0")
        <re.Match object; span=(0, 5), match='1.0.0'>
        >>> match_semver("1.0.0-alpha+001")
        <re.Match object; span=(0, 13), match='1.0.0-alpha+001'>
        >>> match_semver("invalid_version")
        None
    """
    if not pattern:
        pattern = (
            r"(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+(?P<buildmetadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?"
            if strict_semver
            else r"(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)"
        )

    if with_leading_v:
        pattern = f"v{pattern}"
    semver_match = re.match(pattern, version_str)
    return semver_match
