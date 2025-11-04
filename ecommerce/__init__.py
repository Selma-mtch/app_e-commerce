"""Shim de compatibilité exposant les modules du projet sous l'espace de noms « ecommerce.* ».

Ceci permet aux tests d'importer, par exemple, « from ecommerce.models.user import User »
sans restructurer le dépôt. Nous créons des alias pour les paquets et leurs sous‑modules.

Remarque : nous n'aliasons volontairement pas le paquet « web », car son importation
entraîne le chargement d'extensions Flask non nécessaires aux tests et potentiellement
absentes de l'environnement d'intégration continue (CI).
"""

from __future__ import annotations

import importlib
import pkgutil
import sys
from types import ModuleType


def _alias_tree(alias_prefix: str, real_pkg_name: str):
    real_pkg = importlib.import_module(real_pkg_name)
    # Enregistrer le paquet d'alias lui‑même
    sys.modules[alias_prefix] = real_pkg

    # S'il s'agit d'un paquet, parcourir ses sous‑modules et les aliaser également
    if hasattr(real_pkg, "__path__"):
        for finder, full_name, ispkg in pkgutil.walk_packages(real_pkg.__path__, real_pkg.__name__ + "."):
            alias_name = alias_prefix + full_name[len(real_pkg.__name__):]
            try:
                mod = importlib.import_module(full_name)
            except Exception:
                continue
            sys.modules[alias_name] = mod


# S'assurer que le paquet racine existe
sys.modules.setdefault('ecommerce', sys.modules[__name__])

# Créer des alias pour les espaces de noms connus et tous leurs sous‑modules
_alias_tree('ecommerce.models', 'models')
_alias_tree('ecommerce.repositories', 'repositories')
_alias_tree('ecommerce.services', 'services')
