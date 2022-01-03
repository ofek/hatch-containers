# SPDX-FileCopyrightText: 2021-present Ofek Lev <oss@ofek.dev>
#
# SPDX-License-Identifier: MIT
import pytest
from hatch.project.core import Project

from .utils import check_container_output, container_running, dedent, update_project_environment

pytestmark = [pytest.mark.usefixtures('container_cleanup')]


def test_env_vars(hatch, container_project, default_container_name):
    project = Project(container_project)
    update_project_environment(
        project, 'default', {'start-on-creation': True, 'env-vars': {'FOO': 'BAR'}, **project.config.envs['default']}
    )

    with container_project.as_cwd({'FOO': 'BAZ', 'BAR': 'BAZ'}):
        result = hatch(
            'run',
            'python',
            '-c',
            "import pathlib,os;pathlib.Path('/tmp/test.txt').write_text("
            "os.environ.get('FOO','')+'|'+os.environ.get('BAR',''))",
        )

    assert result.exit_code == 0, result.output
    assert result.output == dedent(
        """
        Creating environment: default
        Installing project in development mode
        """
    )
    assert container_running(default_container_name)
    assert check_container_output(default_container_name, ['cat', '/tmp/test.txt']).strip() == 'BAR|'


def test_env_vars_with_include(hatch, container_project, default_container_name):
    project = Project(container_project)
    update_project_environment(
        project,
        'default',
        {
            'start-on-creation': True,
            'env-vars': {'FOO': 'BAR'},
            'env-include': ['FOO', 'BAR'],
            **project.config.envs['default'],
        },
    )

    with container_project.as_cwd({'FOO': 'BAZ', 'BAR': 'BAZ'}):
        result = hatch(
            'run',
            'python',
            '-c',
            "import pathlib,os;pathlib.Path('/tmp/test.txt').write_text("
            "os.environ.get('FOO','')+'|'+os.environ.get('BAR',''))",
        )

    assert result.exit_code == 0, result.output
    assert result.output == dedent(
        """
        Creating environment: default
        Installing project in development mode
        """
    )
    assert container_running(default_container_name)
    assert check_container_output(default_container_name, ['cat', '/tmp/test.txt']).strip() == 'BAR|BAZ'


def test_env_vars_current(hatch, container_project, default_container_name):
    project = Project(container_project)
    update_project_environment(
        project,
        'default',
        {
            'start-on-creation': True,
            'env-vars': {'FOO': 'BAR'},
            'env-include': ['FOO', 'BAR'],
            **project.config.envs['default'],
        },
    )

    with container_project.as_cwd({'FOO': 'BAZ', 'BAR': 'BAZ'}):
        result = hatch(
            'run',
            'python',
            '-c',
            "import pathlib,os;pathlib.Path('/tmp/test.txt').write_text("
            "os.environ.get('FOO','')+'|'+os.environ.get('BAR',''))",
        )

    assert result.exit_code == 0, result.output
    assert result.output == dedent(
        """
        Creating environment: default
        Installing project in development mode
        """
    )
    assert container_running(default_container_name)
    assert check_container_output(default_container_name, ['cat', '/tmp/test.txt']).strip() == 'BAR|BAZ'

    with container_project.as_cwd({'FOO': 'BAZ', 'BAR': 'FOO'}):
        result = hatch(
            'run',
            'python',
            '-c',
            "import pathlib,os;pathlib.Path('/tmp/test.txt').write_text("
            "os.environ.get('FOO','')+'|'+os.environ.get('BAR',''))",
        )

    assert result.exit_code == 0, result.output
    assert not result.output
    assert container_running(default_container_name)
    assert check_container_output(default_container_name, ['cat', '/tmp/test.txt']).strip() == 'BAR|FOO'
