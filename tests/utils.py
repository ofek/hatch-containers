# SPDX-FileCopyrightText: 2021-present Ofek Lev <oss@ofek.dev>
#
# SPDX-License-Identifier: MIT
import subprocess
from textwrap import dedent as _dedent

import tomli
import tomli_w


def dedent(text):
    return _dedent(text[1:])


def check_container_output(container_name, command):
    return subprocess.check_output(['docker', 'exec', container_name, *command]).decode('utf-8')


def container_exists(container_name):
    output = (
        subprocess.check_output(['docker', 'ps', '-a', '--format', '{{.Names}}', '--filter', f'name={container_name}'])
        .strip()
        .decode('utf-8')
    )

    return any(line.strip() == container_name for line in output.splitlines())


def container_running(container_name):
    output = (
        subprocess.check_output(['docker', 'ps', '--format', '{{.Names}}', '--filter', f'name={container_name}'])
        .strip()
        .decode('utf-8')
    )

    return any(line.strip() == container_name for line in output.splitlines())


def update_project_environment(project, name, config):
    project_file = project.root / 'pyproject.toml'
    with open(str(project_file), 'r', encoding='utf-8') as f:
        raw_config = tomli.loads(f.read())

    env_config = raw_config.setdefault('tool', {}).setdefault('hatch', {}).setdefault('envs', {}).setdefault(name, {})
    env_config.update(config)

    project.config.envs[name] = project.config.envs.get(name, project.config.envs['default']).copy()
    project.config.envs[name].update(env_config)

    with open(str(project_file), 'w', encoding='utf-8') as f:
        f.write(tomli_w.dumps(raw_config))
