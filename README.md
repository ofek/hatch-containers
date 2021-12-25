# hatch-containers

| | |
| --- | --- |
| CI/CD | [![CI - Test](https://github.com/ofek/hatch-containers/actions/workflows/test.yml/badge.svg)](https://github.com/ofek/hatch-containers/actions/workflows/test.yml) [![CD - Build](https://github.com/ofek/hatch-containers/actions/workflows/build.yml/badge.svg)](https://github.com/ofek/hatch/actions-containers/workflows/build.yml) |
| Package | [![PyPI - Version](https://img.shields.io/pypi/v/hatch-containers.svg?logo=pypi&label=PyPI&logoColor=gold)](https://pypi.org/project/hatch-containers/) [![PyPI - Python Version](https://img.shields.io/pypi/pyversions/hatch-containers.svg?logo=python&label=Python&logoColor=gold)](https://pypi.org/project/hatch-containers/) |
| Meta | [![code style - black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) [![types - Mypy](https://img.shields.io/badge/types-Mypy-blue.svg)](https://github.com/ambv/black) [![imports - isort](https://img.shields.io/badge/imports-isort-ef8336.svg)](https://github.com/pycqa/isort) [![License - MIT](https://img.shields.io/badge/license-MIT-9400d3.svg)](https://spdx.org/licenses/) [![GitHub Sponsors](https://img.shields.io/github/sponsors/ofek?logo=GitHub%20Sponsors&style=social)](https://github.com/sponsors/ofek) |

-----

This provides a plugin for [Hatch](https://github.com/ofek/hatch) that allows the use of containerized [environments](https://ofek.dev/hatch/latest/environment/).

**Table of Contents**

- [Installation](#installation)
- [Configuration](#configuration)
  - [Python](#python)
  - [Image](#image)
  - [Command](#command)
  - [Startup](#startup)
  - [Shell](#shell)
- [Notes](#notes)
- [Future](#future)
- [License](#license)

## Installation

```console
pip install hatch-containers
```

## Configuration

The [environment plugin](https://ofek.dev/hatch/latest/plugins/environment/) name is `container`.

- ***pyproject.toml***

    ```toml
    [tool.hatch.envs.<ENV_NAME>]
    type = "container"
    ```

- ***hatch.toml***

    ```toml
    [envs.<ENV_NAME>]
    type = "container"
    ```

### Python

If the [Python version](https://ofek.dev/hatch/latest/config/environment/#python-version) is set to a multi-character integer like `310` then it will be interpreted as its `<MAJOR>.<MINOR>` form e.g. `3.10`.

If not set, then the `<MAJOR>.<MINOR>` version of the first `python` found along your `PATH` will be used, defaulting to the Python executable Hatch is running on.

### Image

The `image` option specifies the container image to use e.g. `python:alpine`. It recognizes the placeholder value `{version}` which will be replaced by the value of the [Python option](#python).

Default:

```toml
[envs.<ENV_NAME>]
image = "python:{version}"
```

### Command

The `command` option specifies the command that the container will execute when [started](#startup).

Default:

```toml
[envs.<ENV_NAME>]
command = ["/bin/sleep", "infinity"]
```

### Startup

By default, containers will be started automatically when [entered](https://ofek.dev/hatch/latest/environment/#entering-environments) or when [running commands](https://ofek.dev/hatch/latest/environment/#command-execution) and will be stopped immediately after. If you want containers to start automatically upon [creation](https://ofek.dev/hatch/latest/environment/#creation) and not be stopped until [removal](https://ofek.dev/hatch/latest/environment/#removal), you can set `start-on-creation` to `true`.

Default:

```toml
[envs.<ENV_NAME>]
start-on-creation = false
```

### Shell

The `shell` option specifies the executable that will be used when [entering](https://ofek.dev/hatch/latest/environment/#entering-environments) containers. By default, this is set to `/bin/bash` unless `alpine` is in the [image](#image) name, in which case `/bin/ash` will be used instead.

## Notes

- There must be a `docker` executable along your `PATH`.
- The `env-exclude` [environment variable filter](https://ofek.dev/hatch/latest/config/environment/#filters) has no effect.

## Future

- Support for Windows containers
- Support for building images

## License

`hatch-containers` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
