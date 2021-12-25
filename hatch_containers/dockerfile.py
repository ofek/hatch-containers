# SPDX-FileCopyrightText: 2021-present Ofek Lev <oss@ofek.dev>
#
# SPDX-License-Identifier: MIT
LINUX_TEMPLATE_ENVIRONMENT = """\
FROM {base_image}

RUN python -m pip install --disable-pip-version-check --upgrade virtualenv hatchling \
 && python -m virtualenv /home/venv --no-download --no-periodic-update --pip embed

ENV VIRTUAL_ENV="/home/venv" PATH="/home/venv/bin:$PATH"

WORKDIR /home/project
"""

LINUX_TEMPLATE_BUILDER = """\
FROM {base_image}

RUN python -m pip install --disable-pip-version-check --upgrade virtualenv \
 && python -m virtualenv /home/venv --no-download --no-periodic-update --pip embed

ENV VIRTUAL_ENV="/home/venv" PATH="/home/venv/bin:$PATH"

WORKDIR /home/project

COPY . /home/project
"""


def construct_dockerfile(base_image: str, builder=False):
    if builder:
        return LINUX_TEMPLATE_BUILDER.format(base_image=base_image)
    else:
        return LINUX_TEMPLATE_ENVIRONMENT.format(base_image=base_image)
