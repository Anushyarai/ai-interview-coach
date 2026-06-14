from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

def generate_questions(
    role,
    skills,
    resume_text
):

    prompt = f"""
    Candidate role:
    {role}

    Skills:
    {skills}

    Resume Content:
    {resume_text}

    Generate 5 technical interview questions.

    Return ONLY questions.
    """

    try:

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )

        content = response.text

        questions = content.split("\n")

        cleaned_questions = []

        for q in questions:

            q = q.strip()

            if q:

                cleaned_questions.append(q)

        return cleaned_questions

    except Exception as e:

        print(e)

        # FALLBACK QUESTIONS

        if "firebase" in resume_text.lower():

            return [

                "Explain Firebase Authentication.",

                "How does Firestore work?",

                "Difference between Firebase and SQL databases?"
            ]

        elif "react" in resume_text.lower():

            return [

                "Explain React virtual DOM.",

                "What are React hooks?",

                "Difference between props and state?"
            ]

        elif "machine learning" in resume_text.lower():

            return [

                "Explain supervised learning.",

                "What is overfitting?",

                "Difference between AI and ML?"
            ]

        elif role == "Backend Developer":

            return [

                "Explain REST APIs.",

                "What is Flask routing?",

                "Difference between SQL and NoSQL?"
            ]

        else:

            return [

                "Tell me about yourself.",

                "Explain your strongest project.",

                "Why should we hire you?"
            ]   