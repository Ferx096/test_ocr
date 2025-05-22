import json
import unicodedata
import os
from typing import List, Dict, Tuple, Any
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.neighbors import NearestNeighbors

MODEL_NAME = 'all-MiniLM-L6-v2'

class GlossaryRAG:
    def __init__(self, glossary_path: str):
        self.glossary_path = glossary_path
        self.model = SentenceTransformer(MODEL_NAME)
        self.entries = []  # List[Dict]
        self.embeddings = None
        self.nn = None
        self._load_and_index()

    def _normalize(self, s: str) -> str:
        s = s.lower()
        s = ''.join(c for c in unicodedata.normalize('NFKD', s) if not unicodedata.combining(c))
        s = s.replace('|', ' ').replace('.', ' ').replace(',', ' ')
        s = ' '.join(s.split())
        return s

    def _load_and_index(self):
        with open(self.glossary_path, encoding='utf-8') as f:
            data = json.load(f)
        # Recorrer estructura y términos
        entries = []
        for section, sec_data in data.items():
            estructura = sec_data.get('estructura | structure', {})
            terminos = sec_data.get('terminos', {})
            # Estructura jerárquica
            for struct_name, struct_val in estructura.get('Ejemplo de estructura de Balance general | Example structure of a Balance sheet', {}).items():
                if isinstance(struct_val, dict):
                    for block, sublist in struct_val.items():
                        if isinstance(sublist, list):
                            for sub in sublist:
                                entries.append({'term': self._normalize(sub), 'section': section, 'block': struct_name, 'subblock': block})
                        else:
                            entries.append({'term': self._normalize(sublist), 'section': section, 'block': struct_name, 'subblock': block})
                elif isinstance(struct_val, list):
                    for sub in struct_val:
                        entries.append({'term': self._normalize(sub), 'section': section, 'block': struct_name, 'subblock': None})
                else:
                    entries.append({'term': self._normalize(struct_val), 'section': section, 'block': struct_name, 'subblock': None})
            # Términos y sinónimos
            for term, desc in terminos.items():
                entries.append({'term': self._normalize(term), 'section': section, 'block': None, 'subblock': None, 'desc': desc})
                # Extraer sinónimos del campo desc
                if 'sinónimos' in desc.lower() or 'synonyms' in desc.lower():
                    for part in desc.split('|'):
                        if 'sinónimos' in part.lower() or 'synonyms' in part.lower():
                            syns = part.split(':')[-1].split(',')
                            for syn in syns:
                                entries.append({'term': self._normalize(syn), 'section': section, 'block': None, 'subblock': None, 'desc': desc})
        self.entries = entries
        # Embeddings
        terms = [e['term'] for e in entries]
        self.embeddings = self.model.encode(terms, show_progress_bar=False)
        self.nn = NearestNeighbors(n_neighbors=3, metric='cosine').fit(self.embeddings)

    def query(self, term: str, topk=3) -> List[Dict[str, Any]]:
        norm = self._normalize(term)
        emb = self.model.encode([norm])
        dists, idxs = self.nn.kneighbors(emb, n_neighbors=topk)
        results = []
        for dist, idx in zip(dists[0], idxs[0]):
            entry = self.entries[idx].copy()
            entry['score'] = 1 - dist  # cosine similarity
            results.append(entry)
        return results

# Ejemplo de uso:
# rag = GlossaryRAG('map/map_test.json')
# print(rag.query('caja y bancos'))
