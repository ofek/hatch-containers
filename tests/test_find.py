# SPDX-FileCopyrightText: 2022-present Ofek Lev <oss@ofek.dev>
#
# SPDX-License-Identifier: MIT
import pytest

from .utils import dedent

pytestmark = [pytest.mark.usefixtures('container_cleanup')]


def test(hatch, container_project, default_container_name):
    with container_project.as_cwd():
        result = hatch('env', 'find')

    assert result.exit_code == 0, result.output
    assert result.output == dedent(
        f"""
        {default_container_name}
        """
    )
