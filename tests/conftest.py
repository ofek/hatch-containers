# SPDX-FileCopyrightText: 2021-present Ofek Lev <oss@ofek.dev>
#
# SPDX-License-Identifier: MIT
import os
import sys
from typing import Generator

import pytest
from click.testing import CliRunner as __CliRunner
from hatch.config.constants import AppEnvVars, ConfigEnvVars
from hatch.config.user import ConfigFile
from hatch.project.core import Project
from hatch.utils.fs import Path, temp_directory
from hatch.utils.platform import Platform
from hatch.utils.structures import EnvVars

from .utils import update_project_environment

PLATFORM = Platform()


class CliRunner(__CliRunner):
    def __init__(self, command):
        super().__init__()
        self._command = command

    def __call__(self, *args, **kwargs):
        # Exceptions should always be handled
        kwargs.setdefault('catch_exceptions', False)

        return self.invoke(self._command, args, **kwargs)


@pytest.fixture(scope='session')
def hatch():
    from hatch import cli

    return CliRunner(cli.hatch)


@pytest.fixture(scope='session', autouse=True)
def isolation() -> Generator[Path, None, None]:
    with temp_directory() as d:
        data_dir = d / 'data'
        data_dir.mkdir()
        cache_dir = d / 'cache'
        cache_dir.mkdir()

        default_env_vars = {
            AppEnvVars.NO_COLOR: '1',
            ConfigEnvVars.DATA: str(data_dir),
            ConfigEnvVars.CACHE: str(cache_dir),
            'COLUMNS': '80',
            'LINES': '24',
        }
        with d.as_cwd(default_env_vars):
            os.environ.pop(AppEnvVars.ENV_ACTIVE, None)
            yield d


@pytest.fixture(scope='session')
def data_dir() -> Generator[Path, None, None]:
    yield Path(os.environ[ConfigEnvVars.DATA])


@pytest.fixture(scope='session')
def platform():
    return PLATFORM


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    with temp_directory() as d:
        yield d


@pytest.fixture
def temp_dir_data(temp_dir) -> Generator[Path, None, None]:
    data_path = temp_dir / 'data'
    data_path.mkdir()

    with EnvVars({ConfigEnvVars.DATA: str(data_path)}):
        yield temp_dir


@pytest.fixture(autouse=True)
def config_file(tmp_path) -> ConfigFile:
    path = Path(tmp_path, 'config.toml')
    os.environ[ConfigEnvVars.CONFIG] = str(path)
    config = ConfigFile(path)
    config.restore()
    return config


@pytest.fixture(scope='session')
def default_image():
    return 'python:{version}-slim'


@pytest.fixture(scope='session')
def default_python_version():
    return f'{sys.version_info[0]}.{sys.version_info[1]}'


@pytest.fixture(scope='session')
def default_container_name(project_name, default_python_version):
    return f'{project_name}_default_python_{default_python_version}-slim_{os.getuid()}_{os.getgid()}'


@pytest.fixture(scope='session')
def project_name():
    return os.urandom(12).hex()


@pytest.fixture
def container_cleanup(default_container_name):
    yield

    PLATFORM.run_command(['docker', 'stop', '--time', '0', default_container_name], capture_output=True)
    PLATFORM.run_command(['docker', 'rm', default_container_name], capture_output=True)


@pytest.fixture
def container_project(hatch, temp_dir_data, config_file, project_name, default_image):
    config_file.model.template.plugins['default']['tests'] = False
    config_file.save()

    with temp_dir_data.as_cwd():
        result = hatch('new', project_name)

    assert result.exit_code == 0, result.output

    project_path = temp_dir_data / project_name

    project = Project(project_path)
    config = dict(project.config.envs['default'])
    config.update({'type': 'container', 'image': default_image})
    update_project_environment(project, 'default', config)

    yield project_path
