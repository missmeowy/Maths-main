import os
import re
import pickle
import difflib

import numpy as np
import pandas as pd

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


class HintEngine:

    def __init__(self, csv_path='data/maths_only.csv'):

        self.csv_path = csv_path
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

        self.df = None
        self.embeddings = None

        self._load_data()

    # --------------------------------------------------

    def _clean_text(self, text):

        text = str(text).lower()

        text = text.replace("²", "^2")
        text = text.replace("³", "^3")
        text = text.replace("√", "sqrt")
        text = text.replace("×", "x")
        text = text.replace("÷", "/")

        text = re.sub(r'[^a-z0-9+\-*/^().= ]', ' ', text)
        text = re.sub(r'\s+', ' ', text)

        return text.strip()

    # --------------------------------------------------

    def _load_data(self):

        self.df = pd.read_csv(self.csv_path)

        print(f"\n📊 Total rows : {len(self.df)}")
        print(f"📋 Columns : {self.df.columns.tolist()}")

        required_cols = [
            "question",
            "hint_1",
            "hint_2",
            "hint_3",
            "final_answer"
        ]

        for col in required_cols:

            if col not in self.df.columns:

                raise ValueError(
                    f"Missing column : {col}"
                )

        self.df = self.df.dropna(
            subset=["question"]
        ).reset_index(drop=True)

        print(f"✅ Maths questions loaded : {len(self.df)}")

        cache_file = "data/embeddings_cache.pkl"

        if os.path.exists(cache_file):

            with open(cache_file, "rb") as f:

                self.embeddings = pickle.load(f)

            print("✅ Loaded cached embeddings")

        else:

            print("⏳ Creating embeddings...")

            questions = self.df["question"].fillna("").tolist()

            self.embeddings = self.model.encode(
                questions,
                show_progress_bar=True
            )

            with open(cache_file, "wb") as f:

                pickle.dump(self.embeddings, f)

            print("✅ Embeddings cached")

    # --------------------------------------------------

    def get_hint(self, user_question, top_k=5):

        user_question = self._clean_text(user_question)

        query_embedding = self.model.encode([user_question])

        similarities = cosine_similarity(
            query_embedding,
            self.embeddings
        )[0]

        top_indices = np.argsort(similarities)[::-1][:top_k]

        best_embedding_index = top_indices[0]
        best_embedding_score = similarities[best_embedding_index]

        # -------------------------------
        # Fuzzy Matching
        # -------------------------------

        fuzzy_best_score = 0
        fuzzy_best_index = best_embedding_index

        for idx in top_indices:

            dataset_question = self._clean_text(
                self.df.iloc[idx]["question"]
            )

            score = difflib.SequenceMatcher(
                None,
                user_question,
                dataset_question
            ).ratio()

            if score > fuzzy_best_score:

                fuzzy_best_score = score
                fuzzy_best_index = idx

        if fuzzy_best_score > best_embedding_score:

            best_index = fuzzy_best_index
            best_score = fuzzy_best_score

        else:

            best_index = best_embedding_index
            best_score = best_embedding_score

        best_match = self.df.iloc[best_index]

        hints = self._generate_progressive_hints(best_match)

        if best_score > 0.80:

            confidence = "High"

        elif best_score > 0.55:

            confidence = "Medium"

        else:

            confidence = "Low"

        print("\n" + "=" * 70)
        print("OCR QUESTION")
        print(user_question)
        print()

        print("MATCHED DATASET QUESTION")
        print(best_match["question"])
        print()

        print("CONFIDENCE :", confidence)
        print("SIMILARITY :", round(float(best_score), 4))
        print("=" * 70 + "\n")

        return {

            "found": True,

            "matched_question": best_match.get(
                "question",
                ""
            ),

            "hints": hints,

            "score": float(best_score),

            "confidence": confidence,

            "topic": best_match.get(
                "topic",
                "Mathematics"
            ),

            "class": best_match.get(
                "class",
                ""
            ),

            "final_answer": best_match.get(
                "final_answer",
                ""
            )

        }

    # --------------------------------------------------

    def _generate_progressive_hints(self, row):

        hint_cols = [

            ("💡 Hint 1: ", row.get("hint_1", "")),

            ("🔍 Hint 2: ", row.get("hint_2", "")),

            ("🧩 Hint 3 (Final): ", row.get("hint_3", ""))

        ]

        hints = []

        for label, text in hint_cols:

            text = str(text).strip()

            if text and text.lower() != "nan":

                hints.append(label + text)

        if not hints:

            hints = [
                "Start by recalling the relevant mathematical concept."
            ]

        return hints
