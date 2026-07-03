import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import os
 
 
class HintEngine:
    def __init__(self, csv_path='data/maths_only.csv'):
        self.csv_path = csv_path
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.df = None
        self.embeddings = None
        self._load_data()
 
    def _load_data(self):
        self.df = pd.read_csv(self.csv_path)
 
        print(f"📊 Total rows in CSV: {len(self.df)}")
        print(f"📋 Columns: {self.df.columns.tolist()}")
 
        # Naya dataset pehle se hi maths-only aur clean hai (filtering already
        # done jab dataset banaya tha), isliye yahan dobara keyword filter
        # karne ki zaroorat nahi. Sirf basic safety check: question/hint
        # columns khali na hon.
        required_cols = ['question', 'hint_1', 'hint_2', 'hint_3', 'final_answer']
        for col in required_cols:
            if col not in self.df.columns:
                raise ValueError(
                    f"❌ Expected column '{col}' not found in CSV. "
                    f"Found columns: {self.df.columns.tolist()}"
                )
 
        self.df = self.df.dropna(subset=['question']).reset_index(drop=True)
        print(f"✅ Clean Maths questions loaded: {len(self.df)}")
 
        # Load embeddings from cache or generate fresh
        cache_file = 'data/embeddings_cache.pkl'
        if os.path.exists(cache_file):
            with open(cache_file, 'rb') as f:
                self.embeddings = pickle.load(f)
            print("✅ Embeddings loaded from cache")
        else:
            print("⏳ Generating embeddings... (first time only)")
            questions = self.df['question'].fillna('').tolist()
            self.embeddings = self.model.encode(questions, show_progress_bar=True)
            with open(cache_file, 'wb') as f:
                pickle.dump(self.embeddings, f)
            print("✅ Embeddings cached!")
 
    def get_hint(self, user_question, top_k=3):
        query_embedding = self.model.encode([user_question])
        similarities = cosine_similarity(query_embedding, self.embeddings)[0]
        top_indices = np.argsort(similarities)[::-1][:top_k]
        best_score = similarities[top_indices[0]]
 
        if best_score < 0.45:
            return {
                "found": False,
                "message": "❌ This does not appear to be a Math question, or it is not available in the dataset. Please try a different Math question!",
                "hints": [],
                "score": float(best_score)
            }
 
        best_match = self.df.iloc[top_indices[0]]
        hints = self._generate_progressive_hints(best_match)
 
        return {
            "found": True,
            "matched_question": best_match.get('question', ''),
            "hints": hints,
            "score": float(best_score),
            "topic": best_match.get('topic', 'Mathematics'),
            "class": best_match.get('class', ''),
            "final_answer": best_match.get('final_answer', '')
        }
 
    def _generate_progressive_hints(self, row):
        """Naye dataset mein hints already pre-written hain (hint_1, hint_2,
        hint_3), isliye yahan koi text-splitting nahi karni — bas unhe
        directly emoji labels ke saath return karo."""
        hint_cols = [
            ("💡 Hint 1: ", row.get('hint_1', '')),
            ("🔍 Hint 2: ", row.get('hint_2', '')),
            ("🧩 Hint 3 (Final): ", row.get('hint_3', '')),
        ]
 
        hints = []
        for label, text in hint_cols:
            text = str(text).strip()
            if text and text.lower() != 'nan':
                hints.append(f"{label}{text}")
 
        if not hints:
            hints = ["Start by recalling the basic formula relevant to this question."]
 
        return hints
 