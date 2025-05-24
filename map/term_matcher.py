"""
Clase TermMatcher para hacer matching inteligente de términos contables usando fuzzy matching y embeddings.
Permite asociar términos extraídos a categorías estándar del glosario.
"""
import json
import os
from pathlib import Path
from rapidfuzz import fuzz, process
from langchain_openai import AzureOpenAIEmbeddings
import numpy as np

class TermMatcher:
    def __init__(self, map_json_path=None, embedding_model=None):
        if map_json_path is None:
            map_json_path = str(Path(__file__).parent / "map_test.json")
        with open(map_json_path, encoding="utf-8") as f:
            self.map_data = json.load(f)
        self.embedding_model = embedding_model or AzureOpenAIEmbeddings(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("OPENAI_EMBEDDING_API_VERSION"),
            deployment=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME"),
            model="text-embedding-3-large",
        )
        self._prepare_terms()

    def _prepare_terms(self):
        self.terms = []
        self.term_to_category = {}
        for section, content in self.map_data.items():
            estructura = content.get("estructura, {})
            for block, block_content in estructura.items():
                if isinstance(block_content, dict):
                    for subblock, sublist in block_content.items():
                        if isinstance(sublist, list):
                            for term in sublist:
                                clean_term = term.strip().lower()
                                self.terms.append(clean_term)
                                self.term_to_category[clean_term] = (section, block, subblock)
                        elif isinstance(sublist, str):
                            clean_term = sublist.strip().lower()
                            self.terms.append(clean_term)
                            self.term_to_category[clean_term] = (section, block, subblock)
                elif isinstance(block_content, list):
                    for term in block_content:
                        clean_term = term.strip().lower()
                        self.terms.append(clean_term)
                        self.term_to_category[clean_term] = (section, block, None)
                elif isinstance(block_content, str):
                    clean_term = block_content.strip().lower()
                    self.terms.append(clean_term)
                    self.term_to_category[clean_term] = (section, block, None)
        # Precompute embeddings
        self.term_embeddings = self.embedding_model.embed_documents(self.terms)

    def match(self, query, threshold=70, return_log=False):
        query_clean = query.lower().strip()
        log = {}
        # Fuzzy match
        fuzzy_result = process.extractOne(query_clean, self.terms, scorer=fuzz.token_sort_ratio)
        if fuzzy_result:
            best_fuzzy, score, _ = fuzzy_result
            log['fuzzy'] = {'term': best_fuzzy, 'score': score}
            if score >= threshold:
                if return_log:
                    return best_fuzzy, self.term_to_category[best_fuzzy], score, log
                return best_fuzzy, self.term_to_category[best_fuzzy], score
        # Embedding match
        query_emb = self.embedding_model.embed_query(query_clean)
        sims = np.dot(self.term_embeddings, query_emb) / (np.linalg.norm(self.term_embeddings, axis=1) * np.linalg.norm(query_emb) + 1e-8)
        idx = np.argmax(sims)
        best_emb = self.terms[idx]
        emb_score = sims[idx]
        log['embedding'] = {'term': best_emb, 'score': float(emb_score)}
        if emb_score > 0.7:
            if return_log:
                return best_emb, self.term_to_category[best_emb], emb_score, log
            return best_emb, self.term_to_category[best_emb], emb_score
        if return_log:
            return None, None, 0.0, log
        return None, None, 0.0

    def batch_match(self, queries, threshold=80):
        results = []
        for q in queries:
            results.append(self.match(q, threshold=threshold))
        return results