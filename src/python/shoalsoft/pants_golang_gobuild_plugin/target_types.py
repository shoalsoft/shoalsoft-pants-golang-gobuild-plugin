# Pants Plugin to invoke Official Go toolchain.
# Copyright (C) 2024 Shoal Software LLC. All rights reserved.

from __future__ import annotations

import os
from typing import Iterable, Optional, Sequence

from pants.core.goals.package import OutputPathField
from pants.core.goals.run import RestartableField
from pants.core.goals.test import TestExtraEnvVarsField, TestTimeoutField
from pants.core.util_rules.environments import EnvironmentField
from pants.engine.internals.native_engine import Address
from pants.engine.target import (
    COMMON_TARGET_FIELDS,
    AsyncFieldMixin,
    BoolField,
    Dependencies,
    InvalidFieldException,
    MultipleSourcesField,
    StringField,
    Target,
    ValidNumbers,
    generate_multiple_sources_field_help_message,
)
from pants.util.strutil import help_text


class GoModuleSourcesField(MultipleSourcesField):
    alias = "_sources"
    default = ("go.mod", "go.sum")
    expected_num_files = range(1, 3)  # i.e. 1 or 2.

    @property
    def go_mod_path(self) -> str:
        return os.path.join(self.address.spec_path, "go.mod")

    @property
    def go_sum_path(self) -> str:
        return os.path.join(self.address.spec_path, "go.sum")

    def validate_resolved_files(self, files: Sequence[str]) -> None:
        super().validate_resolved_files(files)
        if self.go_mod_path not in files:
            raise InvalidFieldException(
                f"The {repr(self.alias)} field in target {self.address} must include "
                f"{self.go_mod_path}, but only had: {list(files)}\n\n"
                f"Make sure that you're declaring the `{GoModuleTarget.alias}` target in the same "
                "directory as your `go.mod` file."
            )
        invalid_files = set(files) - {self.go_mod_path, self.go_sum_path}
        if invalid_files:
            raise InvalidFieldException(
                f"The {repr(self.alias)} field in target {self.address} must only include "
                f"`{self.go_mod_path}` and optionally {self.go_sum_path}, but had: "
                f"{sorted(invalid_files)}\n\n"
                f"Make sure that you're declaring the `{GoModuleTarget.alias}` target in the same "
                f"directory as your `go.mod` file and that you don't override the `{self.alias}` "
                "field."
            )


class GoModuleTarget(Target):
    alias = "go_module"
    help = help_text(
        """
        A first-party Go module (corresponding to a `go.mod` file).
        """
    )
    core_fields = (
        *COMMON_TARGET_FIELDS,
        GoModuleSourcesField,
    )


class GoPackageSourcesField(MultipleSourcesField):
    default = ("*.go",)
    expected_file_extensions = (
        ".go",
        ".s",
        ".S",
        ".sx",
        ".c",
        ".h",
        ".hh",
        ".hpp",
        ".hxx",
        ".cc",
        ".cpp",
        ".cxx",
        ".m",
        ".f",
        ".F",
        ".for",
        ".f90",
        ".syso",
    )
    ban_subdirectories = True
    help = generate_multiple_sources_field_help_message(
        "Example: `sources=['example.go', '*_test.go', '!test_ignore.go']`"
    )

    @classmethod
    def compute_value(
        cls, raw_value: Optional[Iterable[str]], address: Address
    ) -> Optional[tuple[str, ...]]:
        value_or_default = super().compute_value(raw_value, address)
        if not value_or_default:
            raise InvalidFieldException(
                f"The {repr(cls.alias)} field in target {address} must be set to files/globs in "
                f"the target's directory, but it was set to {repr(value_or_default)}."
            )
        return value_or_default


class GoPackageDependenciesField(Dependencies):
    pass


class SkipGoTestsField(BoolField):
    alias = "skip_tests"
    default = False
    help = "If true, don't run this package's tests."


class GoTestExtraEnvVarsField(TestExtraEnvVarsField):
    alias = "test_extra_env_vars"


class GoTestTimeoutField(TestTimeoutField):
    alias = "test_timeout"
    valid_numbers = ValidNumbers.positive_and_zero


class GoPackageTarget(Target):
    alias = "go_package"
    core_fields = (
        *COMMON_TARGET_FIELDS,
        GoPackageDependenciesField,
        GoPackageSourcesField,
        GoTestExtraEnvVarsField,
        GoTestTimeoutField,
        SkipGoTestsField,
    )
    help = help_text(
        """
        A first-party Go package (corresponding to a directory with `.go` files).

        Expects that there is a `go_module` target in its directory or in an ancestor
        directory.
        """
    )


# -----------------------------------------------------------------------------------------------
# `go_binary` target
# -----------------------------------------------------------------------------------------------


class GoBinaryMainPackageField(StringField, AsyncFieldMixin):
    alias = "main"
    help = help_text(
        """
        Address of the `go_package` with the `main` for this binary.

        If not specified, will default to the `go_package` for the same
        directory as this target's BUILD file. You should usually rely on this default.
        """
    )
    value: str


class GoBinaryDependenciesField(Dependencies):
    # This is only used to inject a dependency from the `GoBinaryMainPackageField`. Users should
    # add any explicit dependencies to the `go_package`.
    alias = "_dependencies"


class GoBinaryTarget(Target):
    alias = "go_binary"
    core_fields = (
        *COMMON_TARGET_FIELDS,
        OutputPathField,
        GoBinaryMainPackageField,
        GoBinaryDependenciesField,
        # GoCgoEnabledField,
        # GoRaceDetectorEnabledField,
        # GoMemorySanitizerEnabledField,
        # GoAddressSanitizerEnabledField,
        # GoAssemblerFlagsField,
        # GoCompilerFlagsField,
        # GoLinkerFlagsField,
        RestartableField,
        EnvironmentField,
    )
    help = "A Go binary."


# TODO: Remove this field as unnecessary.
class GoImportPathField(StringField):
    alias = "import_path"
    help = help_text(
        """
        Import path in Go code to import this package.

        This field should not be overridden; use the value from target generation.
        """
    )
    required = True
    value: str
