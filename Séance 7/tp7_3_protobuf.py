#!/usr/bin/env python3
"""
TP 7.3 — Protobuf en Python (schéma + échange)
S'appuie sur le fichier document_pb2 généré via:
protoc --python_out=. document.proto
"""

import sys
import json

try:
    import document_pb2
except ImportError:
    print("="*60)
    print("ERREUR : document_pb2 introuvable.")
    print("Vous devez compiler le fichier .proto avant d'exécuter ce script :")
    print("1. Installer protobuf : pip install protobuf")
    print("2. Compiler le proto : protoc --python_out=. document.proto")
    print("="*60)
    sys.exit(1)

def test_protobuf():
    print("=" * 60)
    print("  TP 7.3 — Protobuf en Python")
    print("=" * 60)

    # 1. Encodage (Sérialisation)
    doc = document_pb2.Document()
    doc.id = 42
    doc.title = "Rapport Q1"
    doc.author = "Alice"
    doc.tags.extend(["finance", "interne"])
    doc.classification = "confidential"
    doc.priority = 6  # Nouveau champ
    
    binary_data = doc.SerializeToString()
    print("\n[+] Encodage Protobuf :")
    print(f"  Binaire brut (extrait) : {binary_data[:20].hex()}...")
    print(f"  Taille Protobuf        : {len(binary_data)} octets")

    # 2. Décodage (Désérialisation)
    doc2 = document_pb2.Document()
    doc2.ParseFromString(binary_data)
    
    print("\n[+] Décodage Protobuf :")
    print(f"  Titre          : {doc2.title}")
    print(f"  Tags           : {list(doc2.tags)}")
    print(f"  Priority       : {doc2.priority}")

    # 3. Comparaison avec JSON
    json_data = json.dumps({
        "id": doc.id,
        "title": doc.title,
        "author": doc.author,
        "tags": list(doc.tags),
        "classification": doc.classification,
        "priority": doc.priority
    }, ensure_ascii=False).encode("utf-8")
    
    print("\n[+] Comparaison de taille :")
    print(f"  Taille JSON            : {len(json_data)} octets")
    print(f"  Ratio Protobuf/JSON    : Protobuf est {len(json_data) / len(binary_data):.1f}x plus petit")

    # 4. Compatibilité arrière
    print("\n[+] Test de compatibilité arrière :")
    print("  (Explication : si un lecteur 'v1' qui n'a pas le champ 'priority'")
    print("  lit ce binaire, le champ 'priority' sera traité comme 'Unknown Field'.")
    print("  Il sera stocké en mémoire sans faire crasher l'application.")
    print("  Lors d'une resérialisation par v1, le champ inconnu sera conservé et renvoyé.)")
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_protobuf()
