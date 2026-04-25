#!/usr/bin/env python3
"""
TP 7.2 — Versioning JSON (compatibilité)
Évolution du payload Document d'une v1 vers une v2 sans casser la lecture.
"""

import json
import logging

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

ALLOWED_CLASSIFICATIONS = {"public", "internal", "confidential", "secret"}

def deserialize_document_v2(raw: str) -> dict:
    """
    Désérialiseur V2 acceptant les payloads V1.
    Les champs inconnus sont ignorés (tolérance).
    """
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError("Payload invalide")

    if not isinstance(data, dict):
        raise ValueError("Payload invalide")

    # 1. Champs V1 (obligatoires)
    for f in ("id", "title", "author"):
        if f not in data:
            raise ValueError(f"Champ obligatoire V1 manquant : {f}")

    # 2. Champs V2 (optionnels avec valeurs par défaut)
    tags = data.get("tags", [])
    if not isinstance(tags, list):
        raise ValueError("'tags' doit être une liste")

    classification = data.get("classification", "internal")
    if classification not in ALLOWED_CLASSIFICATIONS:
        raise ValueError("Classification non autorisée")

    # Tolérance aux champs inconnus :
    # On reconstruit un objet uniquement avec les champs de notre contrat.
    # Justification : L'ignorance des champs inconnus (Robustness Principle de Postel)
    # permet à un client v3 d'envoyer des requêtes à ce serveur v2 sans casser le système,
    # tout en évitant d'exposer la base de données à des injections de champs (Mass Assignment).
    
    return {
        "id": data["id"],
        "title": data["title"],
        "author": data["author"],
        "tags": tags,
        "classification": classification
    }

if __name__ == "__main__":
    print("=" * 60)
    print("  TP 7.2 — Versioning JSON")
    print("=" * 60)

    # 1. Payload V1 lu par V2
    print("\n[+] Test : Payload V1 lu par V2")
    payload_v1 = '{"id": 1, "title": "Doc V1", "author": "Alice"}'
    print(f"  Entrée V1 : {payload_v1}")
    print(f"  Sortie V2 : {deserialize_document_v2(payload_v1)}")
    # Résultat attendu : tags=[] et classification="internal"

    # 2. Payload V2 lu par V2
    print("\n[+] Test : Payload V2 lu par V2")
    payload_v2 = '{"id": 2, "title": "Doc V2", "author": "Bob", "tags": ["finance"], "classification": "public"}'
    print(f"  Sortie V2 : {deserialize_document_v2(payload_v2)}")

    # 3. Payload V2 altéré (classification invalide)
    print("\n[-] Test : Payload V2 avec classification 'top_secret'")
    payload_v2_bad = '{"id": 3, "title": "Doc V2", "author": "Charlie", "classification": "top_secret"}'
    try:
        deserialize_document_v2(payload_v2_bad)
    except ValueError as e:
        print(f"  Rejeté avec succès : {e}")

    # 4. Payload V2+ (avec champ inconnu 'priority')
    print("\n[+] Test : Payload avec champ inconnu ('priority')")
    payload_v2_unknown = '{"id": 4, "title": "Doc V2+", "author": "Dave", "priority": "urgent"}'
    print(f"  Entrée V2+: {payload_v2_unknown}")
    print(f"  Sortie V2 : {deserialize_document_v2(payload_v2_unknown)}")
    # Résultat attendu : le champ 'priority' est ignoré et non retourné.
    
    print("\n" + "=" * 60)
