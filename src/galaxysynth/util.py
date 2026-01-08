"""
Utility functions for the package
"""

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
