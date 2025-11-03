"""Compatibility shim exposing project modules under the 'ecommerce.*' namespace.

This lets tests import e.g. 'from ecommerce.models.user import User'
without restructuring the repo. We alias both packages and their submodules.
"""

from __future__ import annotations

import importlib
import pkgutil
import sys
from types import ModuleType


def _alias_tree(alias_prefix: str, real_pkg_name: str):
    real_pkg = importlib.import_module(real_pkg_name)
    # Register the alias package itself
    sys.modules[alias_prefix] = real_pkg

    # If it's a package, walk its submodules and alias them too
    if hasattr(real_pkg, "__path__"):
        for finder, full_name, ispkg in pkgutil.walk_packages(real_pkg.__path__, real_pkg.__name__ + "."):
            alias_name = alias_prefix + full_name[len(real_pkg.__name__):]
            try:
                mod = importlib.import_module(full_name)
            except Exception:
                continue
            sys.modules[alias_name] = mod


# Ensure root package exists
sys.modules.setdefault('ecommerce', sys.modules[__name__])

# Alias known top-level namespaces and all their submodules
_alias_tree('ecommerce.models', 'models')
_alias_tree('ecommerce.repositories', 'repositories')
_alias_tree('ecommerce.services', 'services')
_alias_tree('ecommerce.web', 'web')
