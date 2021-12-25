from hatchling.plugin import hookimpl

from .plugin import ContainerEnvironment


@hookimpl
def hatch_register_environment():
    return ContainerEnvironment
