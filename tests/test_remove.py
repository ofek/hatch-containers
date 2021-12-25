# SPDX-FileCopyrightText: 2021-present Ofek Lev <oss@ofek.dev>
#
# SPDX-License-Identifier: MIT
import pytest
from hatch.project.core import Project

from .utils import container_exists, container_running, update_project_environment

pytestmark = [pytest.mark.usefixtures('container_cleanup')]


def test_not_running(hatch, container_project, default_container_name):
    with container_project.as_cwd():
        result = hatch('env', 'create')

    assert result.exit_code == 0, result.output
    assert container_exists(default_container_name) and not container_running(default_container_name)

    with container_project.as_cwd():
        result = hatch('env', 'remove')

    assert result.exit_code == 0, result.output
    assert not result.output
    assert not container_exists(default_container_name)


def test_running(hatch, container_project, default_container_name):
    project = Project(container_project)
    update_project_environment(project, 'default', {'start-on-creation': True, **project.config.envs['default']})

    with container_project.as_cwd():
        result = hatch('env', 'create')

    assert result.exit_code == 0, result.output
    assert container_running(default_container_name)

    with container_project.as_cwd():
        result = hatch('env', 'remove')

    assert result.exit_code == 0, result.output
    assert not result.output
    assert not container_exists(default_container_name)
