import re
from typing import Dict


def parse_address_fields(address: str | None) -> Dict[str, str]:
    """
    Découpe une adresse multiline en champs structurés (rue, complément, code postal, ville, pays).
    Fonction tolérante : renvoie des chaînes vides si l'information n'est pas trouvée.
    """
    if not address:
        return {"street": "", "line2": "", "postal_code": "", "city": "", "country": ""}

    normalized = address.replace("\\r", "")
    # Gérer les adresses stockées avec les caractères échappés "\n" (chaîne littérale)
    normalized = normalized.replace("\\n", "\n")

    lines = [ln.strip() for ln in normalized.splitlines() if ln.strip()]
    street = lines[0] if lines else ""
    line2 = ""
    postal_code = ""
    city = ""
    country = ""

    remaining = lines[1:] if len(lines) > 1 else []
    def split_postal_city(line: str):
        m = re.match(r"^\s*([0-9A-Za-z-]{4,10})\s+(.+)$", line)
        if not m:
            return None, None
        return m.group(1).strip(), m.group(2).strip()

    # Cas d'une seule ligne : tenter d'extraire code postal / ville à la fin
    if len(lines) == 1:
        tokens = lines[0].split()
        postal_idx = next((i for i, t in enumerate(tokens) if re.fullmatch(r"[0-9][0-9A-Za-z-]{3,9}", t)), None)
        if postal_idx is not None:
            street = " ".join(tokens[:postal_idx]).strip(", ")
            postal_code = tokens[postal_idx]
            city = " ".join(tokens[postal_idx + 1 :]).strip(", ")
        # Si pas de CP détecté, on laisse tout dans street

    # Cherche une ligne de type "75001 Paris" ou "H2X 1Y4 Montréal"
    for idx, ln in enumerate(remaining):
        cp, c = split_postal_city(ln)
        if cp:
            postal_code = cp
            city = c or city
            if idx > 0:
                line2 = " ".join(remaining[:idx]).strip()
            if idx + 1 < len(remaining):
                country = " ".join(remaining[idx + 1 :]).strip()
            break
    else:
        # Pas trouvé de ligne code postal / ville, on place ce qui reste en complément puis pays
        if remaining:
            line2 = remaining[0]
        if len(remaining) >= 2:
            country = remaining[1]

    return {
        "street": street,
        "line2": line2,
        "postal_code": postal_code,
        "city": city,
        "country": country,
    }


def build_address_string(
    street: str,
    line2: str,
    postal_code: str,
    city: str,
    country: str,
) -> str:
    """Assemble les champs en une adresse multilignes destinée au stockage."""
    parts: list[str] = []
    if street.strip():
        parts.append(street.strip())
    if line2.strip():
        parts.append(line2.strip())

    postal_city = " ".join(p for p in [postal_code.strip(), city.strip()] if p)
    if postal_city:
        parts.append(postal_city)
    if country.strip():
        parts.append(country.strip())
    return "\\n".join(parts)
