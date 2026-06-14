from google import genai
from dotenv import load_dotenv
import os
from flask import session

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

def get_adaptive_question(

    performance,

    previous_question,

    previous_answer,

    role
):

    prompt = f"""
    Candidate role: {role}

    Previous question:
    {previous_question}

    Previous answer:
    {previous_answer}

    Performance:
    {performance}

    Generate the NEXT adaptive interview question.

    Return ONLY the question.
    """

    try:

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )

        new_question = response.text.strip()

        # AVOID REPEATING QUESTIONS

        asked_questions = session.get(
            'asked_questions',
            []
        )

        if new_question in asked_questions:

            return "Explain object-oriented programming in Python."

        return new_question

    except Exception as e:

        print(e)

        # FALLBACK QUESTIONS

        fallback_questions = {

            "Needs Improvement": [

                "What is a variable in Python?",

                "Explain what an API is.",

                "What is a database?"
            ],

            "Average": [

                "Explain REST API architecture.",

                "Difference between SQL and NoSQL?",

                "What is Flask routing?"
            ],

            "Excellent": [

                "Explain JWT authentication.",

                "How does database indexing work?",

                "Explain microservices architecture."
            ]
        }

        # GET PREVIOUSLY ASKED QUESTIONS

        asked_questions = session.get(
            'asked_questions',
            []
        )

        # FIND UNUSED QUESTION

        for question in fallback_questions[performance]:

            if question not in asked_questions:

                asked_questions.append(question)

                session['asked_questions'] = asked_questions

                return question

        # DEFAULT

        return "Explain OOP concepts in Python."