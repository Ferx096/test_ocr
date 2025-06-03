import unicodedata
import re
from langchain.schema import Document
from typing import List, Dict, Any

class GlossaryRAGMarkdown:
    def __init__(self, md_path: str, embedding_model):
        self.md_path = md_path
        self.embedding_model = embedding_model
        self.entries = []  # List[Dict[str, Any]]
        self.embeddings = None
        self._parse_and_index()

    def _normalize(self, s: str) -> str:
        s = s.lower()
        s = ''.join(c for c in unicodedata.normalize('NFKD', s) if not unicodedata.combining(c))
        s = s.replace('.', ' ').replace(',', ' ')
        s = ' '.join(s.split())
        return s

    def _parse_and_index(self):
        with open(self.md_path, encoding='utf-8') as f:
            lines = f.readlines()
        current = {}
        field = None
        section = None
        block = None
        subblock = None
        for line in lines:
            l = line.strip()
            # Detectar campos tipo markdown
            m = re.match(r'^(#+) +([a-zA-Z_]+)$', l)
            if m:
                level, campo = len(m.group(1)), m.group(2).lower()
                if level == 2:
                    section = campo
                elif level == 3:
                    block = campo
                elif level == 4:
                    subblock = campo
                elif level == 5:
                    subblock = campo
                elif level == 6:
                    # Si ya hay un término, guardar
                    if 'nombre' in current:
                        self._add_entry(current, section, block, subblock)
                        current = {}
                    field = campo
                else:
                    field = campo
                continue
            # Acumular valores de campo
            if field and l.startswith('- '):
                val = l[2:].strip()
                if field in current:
                    if isinstance(current[field], list):
                        current[field].append(val)
                    else:
                        current[field] = [current[field], val]
                else:
                    current[field] = val
        # Guardar el último término
        if 'nombre' in current:
            self._add_entry(current, section, block, subblock)
        # Generar embeddings
        terms = [e['term'] for e in self.entries]
        self.embeddings = self.embedding_model.encode(terms, show_progress_bar=False)

    def _add_entry(self, current, section, block, subblock):
        # Añadir término principal
        nombre = current.get('nombre')
        if isinstance(nombre, list):
            nombres = nombre
        else:
            nombres = [nombre]
        for n in nombres:
            entry = {
                'term': self._normalize(n),
                'section': section,
                'block': block,
                'subblock': subblock,
                'metadata': {k: v for k, v in current.items() if k != 'nombre'}
            }
            self.entries.append(entry)
        # Añadir sinónimos como entradas independientes
        sinonimos = current.get('sinonimos', [])
        if isinstance(sinonimos, str):
            sinonimos = [sinonimos]
        for s in sinonimos:
            entry = {
                'term': self._normalize(s),
                'section': section,
                'block': block,
                'subblock': subblock,
                'metadata': {k: v for k, v in current.items() if k != 'nombre'}
            }
            self.entries.append(entry)

    def query(self, text: str, topk=3) -> List[Dict[str, Any]]:
        norm = self._normalize(text)
        emb = self.embedding_model.encode([norm])
        import numpy as np
        from sklearn.metrics.pairwise import cosine_similarity
        sims = cosine_similarity(emb, self.embeddings)[0]
        idxs = sims.argsort()[::-1][:topk]
        results = []
        for idx in idxs:
            entry = self.entries[idx].copy()
            entry['score'] = float(sims[idx])
            results.append(entry)
        return results
