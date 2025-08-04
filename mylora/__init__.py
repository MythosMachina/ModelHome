"""Compatibility package for MyLora.

This package re-exports modules from the legacy ``loradb`` package to
provide backward compatibility while the project transitions to the new
name.
"""

from importlib import import_module
import sys

# Re-export top-level modules so ``mylora`` mirrors ``loradb``
_loradb = import_module("loradb")

# Expose selected submodules (extend as needed)
sys.modules[__name__ + ".auth"] = import_module("loradb.auth")
sys.modules[__name__ + ".api"] = import_module("loradb.api")
sys.modules[__name__ + ".agents"] = import_module("loradb.agents")

# Optionally expose attributes from loradb at package level
for attr in getattr(_loradb, "__all__", []):
    globals()[attr] = getattr(_loradb, attr)
