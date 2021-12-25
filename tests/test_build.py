# SPDX-FileCopyrightText: 2021-present Ofek Lev <oss@ofek.dev>
#
# SPDX-License-Identifier: MIT
from .utils import dedent


def test_default_path(hatch, container_project, project_name):
    with container_project.as_cwd():
        result = hatch('build')

    assert result.exit_code == 0, result.output
    assert result.output == dedent(
        f"""
        Setting up build environment
        [sdist]
        dist/{project_name}-0.0.1.tar.gz

        Setting up build environment
        [wheel]
        dist/{project_name}-0.0.1-py3-none-any.whl
        """
    )
    assert (container_project / 'dist' / f'{project_name}-0.0.1.tar.gz').is_file()
    assert (container_project / 'dist' / f'{project_name}-0.0.1-py3-none-any.whl').is_file()


def test_explicit_path(hatch, container_project, project_name):
    build_dir = container_project.parent / 'artifacts'

    with container_project.as_cwd():
        result = hatch('build', str(build_dir))

    assert result.exit_code == 0, result.output
    assert result.output == dedent(
        f"""
        Setting up build environment
        [sdist]
        dist/{project_name}-0.0.1.tar.gz

        Setting up build environment
        [wheel]
        dist/{project_name}-0.0.1-py3-none-any.whl
        """
    )
    assert (build_dir / f'{project_name}-0.0.1.tar.gz').is_file()
    assert (build_dir / f'{project_name}-0.0.1-py3-none-any.whl').is_file()
