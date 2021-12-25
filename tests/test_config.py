# SPDX-FileCopyrightText: 2021-present Ofek Lev <oss@ofek.dev>
#
# SPDX-License-Identifier: MIT
import pytest
from hatch.project.core import Project

from hatch_containers.plugin import ContainerEnvironment


class TestImage:
    def test_default(self, isolation, data_dir, platform):
        env_config = {}
        project = Project(
            isolation,
            config={
                'project': {'name': 'my_app', 'version': '0.0.1'},
                'tool': {'hatch': {'envs': {'default': env_config}}},
            },
        )
        environment = ContainerEnvironment(
            isolation, project.metadata, 'default', project.config.envs['default'], data_dir, platform, 0
        )

        assert environment.config_image == 'python:{version}'

    def test_correct(self, isolation, data_dir, platform):
        env_config = {'image': 'python:{version}-alpine'}
        project = Project(
            isolation,
            config={
                'project': {'name': 'my_app', 'version': '0.0.1'},
                'tool': {'hatch': {'envs': {'default': env_config}}},
            },
        )
        environment = ContainerEnvironment(
            isolation, project.metadata, 'default', project.config.envs['default'], data_dir, platform, 0
        )

        assert environment.config_image == 'python:{version}-alpine'

    def test_not_string(self, isolation, data_dir, platform):
        env_config = {'image': 9000}
        project = Project(
            isolation,
            config={
                'project': {'name': 'my_app', 'version': '0.0.1'},
                'tool': {'hatch': {'envs': {'default': env_config}}},
            },
        )

        with pytest.raises(TypeError, match='Field `tool.hatch.envs.default.image` must be a string'):
            _ = ContainerEnvironment(
                isolation, project.metadata, 'default', project.config.envs['default'], data_dir, platform, 0
            )


class TestCommand:
    def test_default(self, isolation, data_dir, platform):
        env_config = {}
        project = Project(
            isolation,
            config={
                'project': {'name': 'my_app', 'version': '0.0.1'},
                'tool': {'hatch': {'envs': {'default': env_config}}},
            },
        )
        environment = ContainerEnvironment(
            isolation, project.metadata, 'default', project.config.envs['default'], data_dir, platform, 0
        )

        assert environment.config_command == ['/bin/sleep', 'infinity']

    def test_correct(self, isolation, data_dir, platform):
        env_config = {'command': ['/bin/sleep', '9000']}
        project = Project(
            isolation,
            config={
                'project': {'name': 'my_app', 'version': '0.0.1'},
                'tool': {'hatch': {'envs': {'default': env_config}}},
            },
        )
        environment = ContainerEnvironment(
            isolation, project.metadata, 'default', project.config.envs['default'], data_dir, platform, 0
        )

        assert environment.config_command == ['/bin/sleep', '9000']

    def test_not_array(self, isolation, data_dir, platform):
        env_config = {'command': 9000}
        project = Project(
            isolation,
            config={
                'project': {'name': 'my_app', 'version': '0.0.1'},
                'tool': {'hatch': {'envs': {'default': env_config}}},
            },
        )
        environment = ContainerEnvironment(
            isolation, project.metadata, 'default', project.config.envs['default'], data_dir, platform, 0
        )

        with pytest.raises(TypeError, match='Field `tool.hatch.envs.default.command` must be an array'):
            _ = environment.config_command

    def test_argument_not_string(self, isolation, data_dir, platform):
        env_config = {'command': [9000]}
        project = Project(
            isolation,
            config={
                'project': {'name': 'my_app', 'version': '0.0.1'},
                'tool': {'hatch': {'envs': {'default': env_config}}},
            },
        )
        environment = ContainerEnvironment(
            isolation, project.metadata, 'default', project.config.envs['default'], data_dir, platform, 0
        )

        with pytest.raises(TypeError, match='Argument #1 of field `tool.hatch.envs.default.command` must be a string'):
            _ = environment.config_command


class TestPythonVersion:
    def test_default(self, isolation, data_dir, platform, default_python_version):
        env_config = {}
        project = Project(
            isolation,
            config={
                'project': {'name': 'my_app', 'version': '0.0.1'},
                'tool': {'hatch': {'envs': {'default': env_config}}},
            },
        )
        environment = ContainerEnvironment(
            isolation, project.metadata, 'default', project.config.envs['default'], data_dir, platform, 0
        )

        assert environment.python_version == default_python_version

    def test_long(self, isolation, data_dir, platform):
        env_config = {'python': '3.10'}
        project = Project(
            isolation,
            config={
                'project': {'name': 'my_app', 'version': '0.0.1'},
                'tool': {'hatch': {'envs': {'default': env_config}}},
            },
        )
        environment = ContainerEnvironment(
            isolation, project.metadata, 'default', project.config.envs['default'], data_dir, platform, 0
        )

        assert environment.python_version == '3.10'

    def test_short(self, isolation, data_dir, platform):
        env_config = {'python': '310'}
        project = Project(
            isolation,
            config={
                'project': {'name': 'my_app', 'version': '0.0.1'},
                'tool': {'hatch': {'envs': {'default': env_config}}},
            },
        )
        environment = ContainerEnvironment(
            isolation, project.metadata, 'default', project.config.envs['default'], data_dir, platform, 0
        )

        assert environment.python_version == '3.10'


class TestStartOnCreation:
    def test_default(self, isolation, data_dir, platform):
        env_config = {}
        project = Project(
            isolation,
            config={
                'project': {'name': 'my_app', 'version': '0.0.1'},
                'tool': {'hatch': {'envs': {'default': env_config}}},
            },
        )
        environment = ContainerEnvironment(
            isolation, project.metadata, 'default', project.config.envs['default'], data_dir, platform, 0
        )

        assert environment.config_start_on_creation is False

    def test_correct(self, isolation, data_dir, platform):
        env_config = {'start-on-creation': True}
        project = Project(
            isolation,
            config={
                'project': {'name': 'my_app', 'version': '0.0.1'},
                'tool': {'hatch': {'envs': {'default': env_config}}},
            },
        )
        environment = ContainerEnvironment(
            isolation, project.metadata, 'default', project.config.envs['default'], data_dir, platform, 0
        )

        assert environment.config_start_on_creation is True

    def test_not_boolean(self, isolation, data_dir, platform):
        env_config = {'start-on-creation': 9000}
        project = Project(
            isolation,
            config={
                'project': {'name': 'my_app', 'version': '0.0.1'},
                'tool': {'hatch': {'envs': {'default': env_config}}},
            },
        )
        environment = ContainerEnvironment(
            isolation, project.metadata, 'default', project.config.envs['default'], data_dir, platform, 0
        )

        with pytest.raises(TypeError, match='Field `tool.hatch.envs.default.start-on-creation` must be a boolean'):
            _ = environment.config_start_on_creation


class TestShell:
    def test_not_string(self, isolation, data_dir, platform):
        env_config = {'shell': 9000}
        project = Project(
            isolation,
            config={
                'project': {'name': 'my_app', 'version': '0.0.1'},
                'tool': {'hatch': {'envs': {'default': env_config}}},
            },
        )
        environment = ContainerEnvironment(
            isolation, project.metadata, 'default', project.config.envs['default'], data_dir, platform, 0
        )

        with pytest.raises(TypeError, match='Field `tool.hatch.envs.default.shell` must be a string'):
            _ = environment.config_shell

    def test_correct(self, isolation, data_dir, platform):
        env_config = {'shell': 'bash'}
        project = Project(
            isolation,
            config={
                'project': {'name': 'my_app', 'version': '0.0.1'},
                'tool': {'hatch': {'envs': {'default': env_config}}},
            },
        )
        environment = ContainerEnvironment(
            isolation, project.metadata, 'default', project.config.envs['default'], data_dir, platform, 0
        )

        assert environment.config_shell == 'bash'

    def test_default_alpine(self, isolation, data_dir, platform):
        env_config = {'image': 'python:alpine'}
        project = Project(
            isolation,
            config={
                'project': {'name': 'my_app', 'version': '0.0.1'},
                'tool': {'hatch': {'envs': {'default': env_config}}},
            },
        )
        environment = ContainerEnvironment(
            isolation, project.metadata, 'default', project.config.envs['default'], data_dir, platform, 0
        )

        assert environment.config_shell == '/bin/ash'

    def test_default_other(self, isolation, data_dir, platform):
        env_config = {}
        project = Project(
            isolation,
            config={
                'project': {'name': 'my_app', 'version': '0.0.1'},
                'tool': {'hatch': {'envs': {'default': env_config}}},
            },
        )
        environment = ContainerEnvironment(
            isolation, project.metadata, 'default', project.config.envs['default'], data_dir, platform, 0
        )

        assert environment.config_shell == '/bin/bash'
