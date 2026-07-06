import random
import pandas as pd


class PracticeEngine:

    def __init__(self, csv_path="data/maths_only.csv"):

        self.csv_path = csv_path

        self.df = pd.read_csv(csv_path)

        self.df.fillna("", inplace=True)

        print(f"✅ Loaded {len(self.df)} practice questions.")

    # -----------------------------------
    # Get All Subjects
    # -----------------------------------

    def get_subjects(self):

        if "topic" not in self.df.columns:

            return ["Mathematics"]

        subjects = sorted(

            self.df["topic"].dropna().unique().tolist()

        )

        return subjects

    # -----------------------------------
    # Get All Difficulty Levels
    # -----------------------------------

    def get_difficulties(self):

        if "difficulty" not in self.df.columns:

            return [

                "Easy",

                "Medium",

                "Hard"

            ]

        levels = sorted(

            self.df["difficulty"].dropna().unique().tolist()

        )

        return levels

    # -----------------------------------
    # Filter Questions
    # -----------------------------------

    def filter_questions(

        self,

        subject=None,

        difficulty=None

    ):

        data = self.df.copy()

        if subject and "topic" in data.columns:

            data = data[

                data["topic"]

                .str.lower()

                ==

                subject.lower()

            ]

        if difficulty and "difficulty" in data.columns:

            data = data[

                data["difficulty"]

                .str.lower()

                ==

                difficulty.lower()

            ]

        if len(data) == 0:

            data = self.df

        return data.reset_index(drop=True)
        # -----------------------------------
    # Generate Random Question
    # -----------------------------------

    def generate_question(

        self,

        subject=None,

        difficulty=None

    ):

        questions = self.filter_questions(

            subject,

            difficulty

        )

        question = questions.sample(1).iloc[0]

        return {

            "id": int(question.name),

            "question": question.get("question", ""),

            "topic": question.get("topic", "Mathematics"),

            "difficulty": question.get("difficulty", "Medium"),

            "hint_1": question.get("hint_1", ""),

            "hint_2": question.get("hint_2", ""),

            "hint_3": question.get("hint_3", ""),

            "answer": question.get("final_answer", "")

        }

    # -----------------------------------
    # Practice Sessions
    # -----------------------------------

    def create_session(

        self,

        subject=None,

        difficulty=None

    ):

        question = self.generate_question(

            subject,

            difficulty

        )

        return {

            "score": 0,

            "hint_level": 0,

            "question": question

        }

    # -----------------------------------
    # Next Question
    # -----------------------------------

    def next_question(

        self,

        session,

        subject=None,

        difficulty=None

    ):

        session["hint_level"] = 0

        session["question"] = self.generate_question(

            subject,

            difficulty

        )

        return session

    # -----------------------------------
    # Get Hint
    # -----------------------------------

    def get_hint(self, session):

        hints = [

            session["question"]["hint_1"],

            session["question"]["hint_2"],

            session["question"]["hint_3"]

        ]

        level = session["hint_level"]

        if level >= len(hints):

            return {

                "finished": True,

                "hint": "No more hints available."

            }

        session["hint_level"] += 1

        return {

            "finished": False,

            "hint": hints[level]

        }
            # -----------------------------------
    # Normalize Answer
    # -----------------------------------

    def normalize_answer(self, answer):

        return str(answer).strip().lower().replace(" ", "")

    # -----------------------------------
    # Check Student Answer
    # -----------------------------------

    def check_answer(

        self,

        session,

        student_answer

    ):

        correct_answer = self.normalize_answer(

            session["question"]["answer"]

        )

        user_answer = self.normalize_answer(

            student_answer

        )

        correct = user_answer == correct_answer

        if correct:

            session["score"] += 10

            feedback = (

                "🎉 Excellent! Your answer is correct."

            )

        else:

            feedback = (

                "❌ Not quite right. Try using another hint and solve it again."

            )

        return {

            "correct": correct,

            "score": session["score"],

            "feedback": feedback,

            "expected_answer": session["question"]["answer"]

        }

    # -----------------------------------
    # AI Feedback
    # -----------------------------------

    def generate_feedback(

        self,

        session,

        student_answer

    ):

        result = self.check_answer(

            session,

            student_answer

        )

        if result["correct"]:

            return {

                "status": "success",

                "message": result["feedback"],

                "score": result["score"],

                "next_action":

                    "Click Next Question."

            }

        return {

            "status": "try_again",

            "message": result["feedback"],

            "score": result["score"],

            "next_action":

                "Request another hint before submitting again."

        }

    # -----------------------------------
    # Session Statistics
    # -----------------------------------

    def get_statistics(

        self,

        session

    ):

        return {

            "score": session["score"],

            "hint_level": session["hint_level"],

            "current_topic":

                session["question"]["topic"],

            "difficulty":

                session["question"]["difficulty"]

        }
