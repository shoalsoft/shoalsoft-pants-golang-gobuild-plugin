# Pants Plugin to invoke Official Go toolchain.
# Copyright (C) 2024 Shoal Software LLC. All rights reserved.

from pants.engine.target import COMMON_TARGET_FIELDS, AsyncFieldMixin, SingleSourceField, Target
from pants.util.strutil import help_text


class GoModSourceField(SingleSourceField, AsyncFieldMixin):
    alias = "_gomod_source"
    default = None
    required = False
    help = help_text("Marker field")


class GoModuleTarget(Target):
    alias = "go_module"
    help = help_text(
        """
        A first-party Go module (corresponding to a `go.mod` file).
        """
    )
    core_fields = (
        *COMMON_TARGET_FIELDS,
        GoModSourceField,
    )
