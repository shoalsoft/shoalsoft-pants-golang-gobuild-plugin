# Pants Plugin to invoke Official Go toolchain.
# Copyright (C) 2024 Shoal Software LLC. All rights reserved.
import json
from textwrap import dedent  # noqa: PNT20
from typing import Mapping

EXPECTED_VERSION = "1.17"
EXPECTED_VERSION_NEXT_RELEASE = "1.18"


def mock_go_binary(*, version_output: str, env_output: Mapping[str, str]) -> str:
    """Return a bash script that emulates `go version` and `go env`."""
    return dedent(
        f"""\
        #!/bin/bash

        if [[ "$1" == version ]]; then
            echo '{version_output}'
        else
            echo '{json.dumps(env_output)}'
        fi
        """
    )
