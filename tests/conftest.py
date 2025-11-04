"""Garantit la résolution des imports du projet pendant les tests.

Ajoute la racine du dépôt (dossier parent de « tests ») à ``sys.path``
afin que les imports comme ``from ecommerce.models.user import User``
fonctionnent quel que soit l'endroit d'où ``pytest`` est lancé.
"""

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
