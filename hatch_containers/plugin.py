# SPDX-FileCopyrightText: 2021-present Ofek Lev <oss@ofek.dev>
#
# SPDX-License-Identifier: MIT
from __future__ import annotations

import re
import sys
from contextlib import contextmanager

from hatch.env.plugin.interface import EnvironmentInterface
from hatch.utils.fs import Path, temp_directory
from hatch.utils.structures import EnvVars

from .dockerfile import construct_dockerfile


class ContainerEnvironment(EnvironmentInterface):
    PLUGIN_NAME = 'container'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__config_image = None
        self.__config_command = None
        self.__config_start_on_creation = None
        self.__config_shell = None
        self.__python_version = None

        self.base_image = self.config_image.format(version=self.python_version)
        self.base_image_id = re.sub(r'[^\w.-]', '_', self.base_image)
        self.image = f'{self.base_image.replace(":", "_")}:hatch-container'
        self.builder_image = f'{self.image}_builder'
        self.container_name = f'{self.metadata.core.name}_{self.name}'
        self.builder_container_name = f'{self.container_name}_builder'
        self.project_path = '/home/project'

    @staticmethod
    def get_option_types():
        return {'image': str, 'command': list, 'start-on-creation': bool, 'shell': str}

    @property
    def config_image(self):
        if self.__config_image is None:
            image = self.config.get('image', 'python:{version}')
            if not isinstance(image, str):
                raise TypeError(f'Field `tool.hatch.envs.{self.name}.image` must be a string')

            self.__config_image = image

        return self.__config_image

    @property
    def config_command(self):
        if self.__config_command is None:
            command = self.config.get('command', ['/bin/sleep', 'infinity'])
            if not isinstance(command, list):
                raise TypeError(f'Field `tool.hatch.envs.{self.name}.command` must be an array')

            for i, arg in enumerate(command, 1):
                if not isinstance(arg, str):
                    raise TypeError(f'Argument #{i} of field `tool.hatch.envs.{self.name}.command` must be a string')

            self.__config_command = command

        return self.__config_command

    @property
    def config_start_on_creation(self):
        if self.__config_start_on_creation is None:
            start_on_creation = self.config.get('start-on-creation', False)
            if not isinstance(start_on_creation, bool):
                raise TypeError(f'Field `tool.hatch.envs.{self.name}.start-on-creation` must be a boolean')

            self.__config_start_on_creation = start_on_creation

        return self.__config_start_on_creation

    @property
    def config_shell(self):
        if self.__config_shell is None:
            shell = self.config.get('shell', '')
            if not isinstance(shell, str):
                raise TypeError(f'Field `tool.hatch.envs.{self.name}.shell` must be a string')

            if not shell:
                if 'alpine' in self.base_image:
                    shell = '/bin/ash'
                else:
                    shell = '/bin/bash'

            self.__config_shell = shell

        return self.__config_shell

    @property
    def python_version(self):
        if self.__python_version is None:
            python_version = self.config.get('python', '')
            if not python_version:
                python_version = '.'.join(map(str, sys.version_info[:2]))
            elif python_version.isdigit() and len(python_version) > 1:
                python_version = f'{python_version[0]}.{python_version[1:]}'

            self.__python_version = python_version

        return self.__python_version

    def _activate(self):
        self.platform.check_command_output(['docker', 'start', self.container_name])

    def _deactivate(self):
        self.platform.check_command_output(['docker', 'stop', '--time', '0', self.container_name])

    def activate(self):
        if not self.config_start_on_creation:
            self._activate()

    def deactivate(self):
        if not self.config_start_on_creation:
            self._deactivate()

    def create(self):
        build_dir = self.data_directory / 'dockerfiles' / self.base_image_id
        dockerfile = build_dir / 'Dockerfile'
        build_dir.ensure_dir_exists()
        dockerfile.write_text(construct_dockerfile(self.base_image))

        command = ['docker', 'build', '--pull', '--tag', self.image, '--file', dockerfile, build_dir]
        if self.verbosity > 0:  # no cov
            self.platform.check_command(command)
        else:
            self.platform.check_command_output(command)

        # fmt: off
        command = [
            'docker', 'create',
            '--name', self.container_name,
            '--workdir', self.project_path,
            '--volume', f'{self.root}:{self.project_path}',
        ]
        # fmt: on

        self.apply_env_vars(command)
        command.append(self.image)
        command.extend(self.config_command)

        self.platform.check_command_output(command)

        if self.config_start_on_creation:
            self._activate()

    def remove(self):
        if self.config_start_on_creation:
            self._deactivate()

        self.platform.check_command_output(['docker', 'rm', self.container_name])

    def exists(self):
        output = self.platform.check_command_output(
            ['docker', 'ps', '-a', '--format', '{{.Names}}', '--filter', f'name={self.container_name}']
        )

        return any(line.strip() == self.container_name for line in output.splitlines())

    def install_project(self):
        with self:
            self.platform.check_command(self.construct_pip_install_command([self.apply_features(self.project_path)]))

    def install_project_dev_mode(self):
        with self:
            self.platform.check_command(
                self.construct_pip_install_command(['--editable', self.apply_features(self.project_path)])
            )

    def dependencies_in_sync(self):
        if not self.dependencies:
            return True

        with self:
            process = self.platform.run_command(
                self.construct_container_command(['hatchling', 'dep', 'synced', '-p', 'python', *self.dependencies]),
                capture_output=True,
            )
            return not process.returncode

    def sync_dependencies(self):
        with self:
            self.platform.check_command(self.construct_pip_install_command(self.dependencies))

    def run_shell_commands(self, commands):
        with self:
            for command in self.resolve_commands(commands):
                yield self.platform.run_command(self.construct_container_shell_command(command))

    def enter_shell(self, name, path):  # no cov
        with self:
            process = self.platform.run_command(self.construct_container_command([self.config_shell], interactive=True))
            self.platform.exit_with_code(process.returncode)

    @contextmanager
    def build_environment(self, dependencies: list[str]):
        with temp_directory() as temp_dir:
            dockerfile = temp_dir / 'Dockerfile'
            dockerfile.write_text(construct_dockerfile(self.base_image, builder=True))

            command = ['docker', 'build', '--pull', '--tag', self.builder_image, '--file', dockerfile, str(self.root)]
            if self.verbosity > 0:  # no cov
                self.platform.check_command(command)
            else:
                self.platform.check_command_output(command)

            local_artifact_dir = temp_dir / 'artifacts'
            container_artifact_dir = f'{self.project_path}/dist'

            # fmt: off
            command = [
                'docker', 'create',
                '--name', self.builder_container_name,
                '--workdir', self.project_path,
            ]
            # fmt: on

            self.apply_env_vars(command)
            command.append(self.builder_image)
            command.extend(self.config_command)

            self.platform.check_command_output(command)
            try:
                self.platform.check_command_output(['docker', 'start', self.builder_container_name])
                self.platform.check_command(self.construct_builder_pip_install_command(dependencies))

                data = {'output_dir': ''}
                yield data

                output_dir = Path(data['output_dir'])
                output_dir.ensure_dir_exists()

                self.platform.check_command_output(
                    ['docker', 'cp', f'{self.builder_container_name}:{container_artifact_dir}', local_artifact_dir]
                )

                for artifact in local_artifact_dir.iterdir():
                    artifact.replace(output_dir / artifact.name)
            finally:
                self.platform.run_command(
                    ['docker', 'stop', '--time', '0', self.builder_container_name], capture_output=True
                )
                self.platform.run_command(['docker', 'rm', self.builder_container_name], capture_output=True)

    def get_build_process(self, build_environment, **kwargs):
        build_environment['output_dir'] = kwargs.pop('directory', '') or str(self.root / 'dist')

        return self.platform.capture_process(self.construct_builder_command(self.construct_build_command(**kwargs)))

    def finalize_command(self, command):
        return command

    def construct_pip_install_command(self, *args, **kwargs):
        return self.construct_container_command(super().construct_pip_install_command(*args, **kwargs))

    def construct_builder_pip_install_command(self, *args, **kwargs):
        return self.construct_builder_command(super().construct_pip_install_command(*args, **kwargs))

    def get_container_env_vars(self) -> dict:
        if self.env_include:
            return dict(EnvVars(self.env_vars, self.env_include))
        else:
            return dict(self.env_vars)

    def construct_container_command(self, args, interactive=False):
        command = ['docker', 'exec']
        if interactive:  # no cov
            command.append('-it')

        self.apply_env_vars(command)
        command.append(self.container_name)
        command.extend(args)
        return command

    def construct_builder_command(self, args):
        command = ['docker', 'exec']

        self.apply_env_vars(command)
        command.append(self.builder_container_name)
        command.extend(args)
        return command

    def apply_env_vars(self, command):
        # This ensures that all commands that are executed have access to the environment variables
        # that are currently defined at all times. Note that we create the images with the environment
        # variables defined at that time only for debugging purposes if users for some reason enter
        # the containers manually rather than using the `hatch shell` command.
        for env_var, value in self.get_container_env_vars().items():
            command.extend(('--env', f'{env_var}={value}'))

    def construct_container_shell_command(self, command):
        return self.construct_container_command(['sh', '-c', command])
