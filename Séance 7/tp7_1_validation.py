#!/usr/bin/env python3
"""
TP 7.1 — Contrat JSON + Validation Stricte (API)
Modeles : Document et UserPublic
Validation exhaustive et approche "fail closed".
"""

import json
import logging
import re
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import List, Optional

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────
# CONSTANTES & REGLES
# ──────────────────────────────────────────────
ALLOWED_CLASSIFICATIONS = {"public", "internal", "confidential", "secret"}
ALLOWED_ROLES = {"viewer", "editor", "admin"}
USERNAME_REGEX = re.compile(r"^[a-zA-Z0-9_]{3,30}$")

# ──────────────────────────────────────────────
# MODELES
# ──────────────────────────────────────────────
@dataclass
class Document:
    id: int
    title: str
    author: str
    tags: List[str] = field(default_factory=list)
    classification: str = "internal"
    created_at: Optional[str] = None
    
    # Champ sensible ajoute pour verifier la non-serialisation
    _internal_note: str = field(default="", repr=False)

@dataclass
class UserPublic:
    username: str
    display_name: str
    role: str
    
    # Champ prive pour simuler un champ sensible
    _password_hash: str = field(default="", repr=False)


# ──────────────────────────────────────────────
# SERIALISATION
# ──────────────────────────────────────────────
def serialize_document(doc: Document) -> str:
    """Serialise en ignorant les champs prives (commencant par '_')."""
    data = {k: v for k, v in asdict(doc).items() if not k.startswith("_")}
    return json.dumps(data, ensure_ascii=False)

def serialize_user(user: UserPublic) -> str:
    data = {k: v for k, v in asdict(user).items() if not k.startswith("_")}
    return json.dumps(data, ensure_ascii=False)


# ──────────────────────────────────────────────
# DESERIALISATION & VALIDATION (DOCUMENT)
# ──────────────────────────────────────────────
def deserialize_document(raw: str) -> Document:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        logger.warning("JSON invalide (Document) : %s", e)
        raise ValueError("Payload invalide")

    if not isinstance(data, dict):
        raise ValueError("Payload invalide")

    errors = []

    # 1. ID (int, > 0)
    if "id" not in data:
        errors.append("Champ 'id' manquant")
    elif not isinstance(data["id"], int) or data["id"] <= 0:
        errors.append("'id' doit etre un entier positif > 0")

    # 2. Title (str, 1-200, non vide apres strip)
    if "title" not in data:
        errors.append("Champ 'title' manquant")
    elif not isinstance(data["title"], str):
        errors.append("'title' doit etre une chaine")
    else:
        title_stripped = data["title"].strip()
        if len(title_stripped) == 0 or len(title_stripped) > 200:
            errors.append("'title' doit faire entre 1 et 200 caracteres (non vide)")

    # 3. Author (str, 1-100)
    if "author" not in data:
        errors.append("Champ 'author' manquant")
    elif not isinstance(data["author"], str):
        errors.append("'author' doit etre une chaine")
    else:
        if len(data["author"]) < 1 or len(data["author"]) > 100:
            errors.append("'author' doit faire entre 1 et 100 caracteres")

    # 4. Tags (list[str], max 20, 1-50 chars)
    tags = data.get("tags", [])
    if not isinstance(tags, list):
        errors.append("'tags' doit etre une liste")
    elif len(tags) > 20:
        errors.append("Maximum 20 tags autorises")
    else:
        for t in tags:
            if not isinstance(t, str):
                errors.append("Chaque tag doit etre une chaine")
                break
            if len(t) < 1 or len(t) > 50:
                errors.append("Chaque tag doit faire entre 1 et 50 caracteres")
                break

    # 5. Classification (allowlist)
    classification = data.get("classification", "internal")
    if classification not in ALLOWED_CLASSIFICATIONS:
        errors.append(f"Classification invalide. Permis: {ALLOWED_CLASSIFICATIONS}")

    # 6. Created_at (ISO 8601)
    created_at = data.get("created_at")
    if created_at is not None:
        if not isinstance(created_at, str):
            errors.append("'created_at' doit etre une chaine")
        else:
            try:
                # Basic ISO 8601 parsing validation (ending with Z for UTC)
                if not created_at.endswith("Z"):
                    raise ValueError
                datetime.fromisoformat(created_at[:-1])
            except ValueError:
                errors.append("Format 'created_at' invalide (attendu ISO 8601 YYYY-MM-DDTHH:MM:SSZ)")

    # Fail closed en cas d'erreur
    if errors:
        logger.warning("Validation Document echouee : %s", errors)
        raise ValueError("Payload invalide")

    return Document(
        id=data["id"],
        title=data["title"].strip(),
        author=data["author"],
        tags=tags,
        classification=classification,
        created_at=created_at
    )


# ──────────────────────────────────────────────
# DESERIALISATION & VALIDATION (USER)
# ──────────────────────────────────────────────
def deserialize_user(raw: str) -> UserPublic:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        logger.warning("JSON invalide (User) : %s", e)
        raise ValueError("Payload invalide")

    if not isinstance(data, dict):
        raise ValueError("Payload invalide")

    errors = []

    # 1. Username (3-30, alphanum + _)
    if "username" not in data:
        errors.append("Champ 'username' manquant")
    elif not isinstance(data["username"], str) or not USERNAME_REGEX.match(data["username"]):
        errors.append("'username' invalide (3-30 chars, alphanumerique et underscore)")

    # 2. Display Name (1-100)
    if "display_name" not in data:
        errors.append("Champ 'display_name' manquant")
    elif not isinstance(data["display_name"], str) or len(data["display_name"]) < 1 or len(data["display_name"]) > 100:
        errors.append("'display_name' doit faire entre 1 et 100 caracteres")

    # 3. Role (allowlist)
    if "role" not in data:
        errors.append("Champ 'role' manquant")
    elif data["role"] not in ALLOWED_ROLES:
        errors.append(f"Role invalide. Permis: {ALLOWED_ROLES}")

    if errors:
        logger.warning("Validation User echouee : %s", errors)
        raise ValueError("Payload invalide")

    return UserPublic(
        username=data["username"],
        display_name=data["display_name"],
        role=data["role"]
    )


# ──────────────────────────────────────────────
# TESTS DU TP
# ──────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("  TP 7.1 — Contrat JSON + Validation")
    print("=" * 60)

    # 1. Cas Valide - Document Complet
    print("\n[+] Test 1 : Document valide (complet)")
    doc_json = '{"id": 42, "title": "  Rapport Q1  ", "author": "Alice Dupont", "tags": ["finance", "2026"], "classification": "confidential", "created_at": "2026-01-15T10:30:00Z"}'
    doc1 = deserialize_document(doc_json)
    print(f"  OK -> {doc1}")
    print(f"  Note: Le titre a bien ete strippe: '{doc1.title}'")

    # 2. Cas Valide - UserPublic
    print("\n[+] Test 2 : UserPublic valide")
    user_json = '{"username": "alice_d", "display_name": "Alice Dupont", "role": "editor"}'
    user1 = deserialize_user(user_json)
    print(f"  OK -> {user1}")
    
    # On ajoute un champ prive dynamiquement pour voir s'il est ignore a la serialisation
    user1._password_hash = "abc123secret"
    print(f"  Serialise (sans _password_hash): {serialize_user(user1)}")

    # 3. Cas Invalide - Champ manquant (Document)
    print("\n[-] Test 3 : Document sans 'title' (champ manquant)")
    try:
        deserialize_document('{"id": 1, "author": "Alice"}')
    except ValueError as e:
        print(f"  Rejete avec succes : {e}")

    # 4. Cas Invalide - Type erroné + format (User)
    print("\n[-] Test 4 : UserPublic avec username invalide (trop court + car. speciaux)")
    try:
        deserialize_user('{"username": "a@", "display_name": "A", "role": "viewer"}')
    except ValueError as e:
        print(f"  Rejete avec succes : {e}")

    # 5. Cas Invalide - Valeur hors allowlist (Document)
    print("\n[-] Test 5 : Document avec classification inconnue")
    try:
        deserialize_document('{"id": 10, "title": "Test", "author": "Bob", "classification": "ultra_secret"}')
    except ValueError as e:
        print(f"  Rejete avec succes : {e}")

    # 6. Cas Invalide - ID negatif (Document)
    print("\n[-] Test 6 : Document avec ID negatif")
    try:
        deserialize_document('{"id": -5, "title": "X", "author": "Y"}')
    except ValueError as e:
        print(f"  Rejete avec succes : {e}")
        
    print("\n" + "=" * 60)
    print("  Tests du TP termines.")
    print("=" * 60)
