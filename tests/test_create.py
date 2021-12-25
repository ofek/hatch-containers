# SPDX-FileCopyrightText: 2021-present Ofek Lev <oss@ofek.dev>
#
# SPDX-License-Identifier: MIT
import pytest
from hatch.project.core import Project

from .utils import check_container_output, container_exists, container_running, dedent, update_project_environment

pytestmark = [pytest.mark.usefixtures('container_cleanup')]


def test_basic(hatch, container_project, default_container_name):
    assert not container_exists(default_container_name)

    with container_project.as_cwd():
        result = hatch('env', 'create')

    assert result.exit_code == 0, result.output
    assert result.output == dedent(
        """
        Creating environment: default
        Installing project in development mode
        """
    )
    assert container_exists(default_container_name) and not container_running(default_container_name)


def test_already_exists(hatch, container_project):
    with container_project.as_cwd():
        result = hatch('env', 'create')

    assert result.exit_code == 0, result.output

    with container_project.as_cwd():
        result = hatch('env', 'create')

    assert result.exit_code == 0, result.output
    assert result.output == dedent(
        """
        Environment `default` already exists
        """
    )


def test_start_on_creation(hatch, container_project, default_container_name, project_name):
    project = Project(container_project)
    update_project_environment(project, 'default', {'start-on-creation': True, **project.config.envs['default']})

    with container_project.as_cwd():
        result = hatch('env', 'create')

    assert result.exit_code == 0, result.output
    assert result.output == dedent(
        """
        Creating environment: default
        Installing project in development mode
        """
    )
    assert container_running(default_container_name)

    output = check_container_output(default_container_name, ['python', '-m', 'pip', 'freeze'])
    lines = output.strip().splitlines()

    assert len(lines) == 3
    lines.remove(f'# Editable install with no version control ({project_name}==0.0.1)')
    lines.remove('-e /home/project')
    assert lines[0].startswith('editables==')


def test_no_dev_mode(hatch, container_project, default_container_name, project_name):
    project = Project(container_project)
    update_project_environment(
        project, 'default', {'dev-mode': False, 'start-on-creation': True, **project.config.envs['default']}
    )

    with container_project.as_cwd():
        result = hatch('env', 'create')

    assert result.exit_code == 0, result.output
    assert result.output == dedent(
        """
        Creating environment: default
        Installing project
        """
    )
    assert container_running(default_container_name)

    assert check_container_output(default_container_name, ['python', '-m', 'pip', 'freeze']) == dedent(
        f"""
        {project_name} @ file:///home/project
        """
    )


def test_dependencies(hatch, container_project, default_container_name, project_name):
    project = Project(container_project)
    update_project_environment(
        project,
        'default',
        {'dev-mode': False, 'start-on-creation': True, 'dependencies': ['binary'], **project.config.envs['default']},
    )

    with container_project.as_cwd():
        result = hatch('env', 'create')

    assert result.exit_code == 0, result.output
    assert result.output == dedent(
        """
        Creating environment: default
        Installing project
        Syncing dependencies
        """
    )
    assert container_running(default_container_name)

    output = check_container_output(default_container_name, ['python', '-m', 'pip', 'freeze'])
    lines = output.strip().splitlines()

    assert len(lines) == 2
    lines.remove(f'{project_name} @ file:///home/project')
    assert lines[0].startswith('binary==')
