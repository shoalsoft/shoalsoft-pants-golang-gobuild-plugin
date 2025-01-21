# Pants Plugin to invoke Official Go toolchain.
# Copyright (C) 2024 Shoal Software LLC. All rights reserved.

from pants.option.option_types import StrListOption, StrOption
from pants.option.subsystem import Subsystem
from pants.util.strutil import softwrap


class GolangSubsystem(Subsystem):
    options_scope = "golang2"
    help = "Options for Golang support."

    class EnvironmentAware(Subsystem.EnvironmentAware):
        env_vars_used_by_options = ("PATH",)

        _go_search_paths = StrListOption(
            default=["<PATH>"],
            help=softwrap(
                """
                A list of paths to search for Go.

                Specify absolute paths to directories with the `go` binary, e.g. `/usr/bin`.
                Earlier entries will be searched first.

                The following special strings are supported:

                * `<PATH>`, the contents of the PATH environment variable
                """
            ),
        )

        @property
        def raw_go_search_paths(self) -> tuple[str, ...]:
            return tuple(self._go_search_paths)

    minimum_expected_version = StrOption(
        default="1.17",
        help=softwrap(
            """
            The minimum Go version the distribution discovered by Pants must support.

            For example, if you set `'1.17'`, then Pants will look for a Go binary that is 1.17+,
            e.g. 1.17 or 1.18.

            You should still set the Go version for each module in your `go.mod` with the `go`
            directive.

            Do not include the patch version.
            """
        ),
    )
