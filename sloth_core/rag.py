"""
Local RAG (Retrieval-Augmented Generation) for SlothDesk.
Lets users query their entire digital hoard in plain English without cloud services.
"""

import math
import re
from typing import List, Dict, Any
from sloth_core.organizer import SlothOrganizer
from sloth_core.engine import SlothAIEngine

class SlothRAG:
    def __init__(self, organizer: SlothOrganizer):
        self.organizer = organizer
        self.ai_engine = organizer.ai_engine

    def _tokenize(self, text: str) -> List[str]:
        return [w.lower() for w in re.findall(r"\b\w{2,}\b", text)]

    def search_files(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Fast local BM25/TF-IDF semantic relevance ranking over local files.
        Zero dependencies, zero cloud API calls.
        """
        files = self.organizer.get_all_files()
        if not files:
            return []

        query_tokens = self._tokenize(query)
        if not query_tokens:
            return files[:top_k]

        # Fetch excerpts from DB
        with self.organizer._get_connection() as conn:
            cursor = conn.cursor()
            scored_files = []
            for f in files:
                cursor.execute("SELECT content_excerpt FROM files WHERE id = ?", (f["id"],))
                row = cursor.fetchone()
                excerpt = row["content_excerpt"] if row else ""

                doc_text = f"{f['current_name']} {f['original_name']} {f['category']} {f['summary']} {' '.join(f.get('tags', []))} {excerpt}"
                doc_tokens = self._tokenize(doc_text)
                doc_len = max(len(doc_tokens), 1)

                # Scoring
                score = 0.0
                for qt in query_tokens:
                    tf = doc_tokens.count(qt)
                    if tf > 0:
                        # BM25-like saturation
                        score += (tf * 2.2) / (tf + 1.2 * (0.25 + 0.75 * (doc_len / 100.0)))

                # Exact phrase bonus
                if query.lower() in doc_text.lower():
                    score += 5.0

                # Action bonus if user asked about bills / tasks
                if ("bill" in query.lower() or "pay" in query.lower()) and f.get("category") == "finance":
                    score += 2.0
                if ("meeting" in query.lower() or "action" in query.lower()) and f.get("category") == "work":
                    score += 2.0

                if score > 0:
                    scored_files.append((score, {
                        "id": f["id"],
                        "name": f["current_name"],
                        "category": f["category"],
                        "summary": f["summary"],
                        "content_excerpt": excerpt[:800],
                        "tags": f.get("tags", []),
                        "relevance_score": round(score, 2)
                    }))

            scored_files.sort(key=lambda x: x[0], reverse=True)
            return [item[1] for item in scored_files[:top_k]]

    def ask(self, query: str) -> Dict[str, Any]:
        """Performs local retrieval and calls local AI engine for lazy human response."""
        relevant_docs = self.search_files(query, top_k=4)
        return self.ai_engine.answer_query(query, relevant_docs)
