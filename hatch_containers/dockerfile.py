# SPDX-FileCopyrightText: 2021-present Ofek Lev <oss@ofek.dev>
#
# SPDX-License-Identifier: MIT
LINUX_TEMPLATE_ENVIRONMENT = """\
FROM {base_image}
ARG USER_UID
ARG USER_GID

RUN set -eux; \
    if ! getent group $USER_GID >/dev/null 2>&1; then \
        addgroup --gid $USER_GID user; \
    fi; \
    if ! getent passwd $USER_UID >/dev/null 2>&1; then \
        adduser --disabled-password --gecos "" --home /home/user --ingroup user --uid "$USER_UID" user; \
    fi

USER $USER_UID:$USER_GID
RUN set -eux; \
    python -m pip install --disable-pip-version-check --upgrade virtualenv hatchling; \
    python -m virtualenv /home/user/venv --no-download --no-periodic-update --pip embed

ENV VIRTUAL_ENV="/home/user/venv" PATH="/home/user/venv/bin:$PATH"

WORKDIR /home/project
"""

LINUX_TEMPLATE_BUILDER = """\
FROM {base_image}
ARG USER_UID
ARG USER_GID

RUN set -eux; \
    if ! getent group $USER_GID >/dev/null 2>&1; then \
        addgroup --gid $USER_GID user; \
    fi; \
    if ! getent passwd $USER_UID >/dev/null 2>&1; then \
        adduser --disabled-password --gecos "" --home /home/user --ingroup user --uid "$USER_UID" user; \
    fi

USER $USER_UID:$USER_GID
RUN set -eux; \
    python -m pip install --disable-pip-version-check --upgrade virtualenv hatchling; \
    python -m virtualenv /home/user/venv --no-download --no-periodic-update --pip embed

ENV VIRTUAL_ENV="/home/user/venv" PATH="/home/user/venv/bin:$PATH"

WORKDIR /home/project

COPY --chown=$USER_UID:$USER_GID . /home/project
"""


def construct_dockerfile(base_image: str, *, builder=False):
    if builder:
        return LINUX_TEMPLATE_BUILDER.format(base_image=base_image)
    else:
        return LINUX_TEMPLATE_ENVIRONMENT.format(base_image=base_image)
