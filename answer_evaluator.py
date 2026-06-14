from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

def evaluate_answer(answer):

    cleaned_answer = answer.lower().strip()

    prompt = f"""
    Evaluate this interview answer.

    Answer:
    {answer}

    Return EXACTLY:

    Score: x/10
    Performance: level

    Feedback:
    point 1
    point 2
    point 3
    """

    try:

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )

        content = response.text

        lines = content.split("\n")

        score = 0
        performance = "Average"
        feedback = []

        for line in lines:

            if "Score:" in line:

                try:

                    score = int(
                        line.split(":")[1]
                        .split("/")[0]
                        .strip()
                    )

                except:

                    score = 5

            elif "Performance:" in line:

                performance = line.split(":")[1].strip()

            elif (
                line.strip()
                and "Feedback" not in line
            ):

                feedback.append(
                    line.strip()
                )

        return score, feedback, performance

    except Exception as e:

        print(e)

        # VERY WEAK ANSWERS

        weak_answers = [

            "idk",
            "i dont know",
            "don't know",
            "not known",
            "no idea",
            "nahi pata",
            "?",
            "s",
            "f",
            "a",
            "b",
            "c",
            "d",
            "x",
            "y",
            "z",
            ".",
            "..",
            "..."
        ]

        if (
            cleaned_answer in weak_answers
            or len(cleaned_answer) <= 2
        ):

            return (

                0,

                [

                    "Answer indicates no understanding.",

                    "Try learning the concept first.",

                    "Give at least a basic technical explanation."
                ],

                "Needs Improvement"
            )

        # WORD COUNT

        word_count = len(
            cleaned_answer.split()
        )

        # TECHNICAL KEYWORDS

        technical_keywords = [

            "api",
            "database",
            "python",
            "flask",
            "sql",
            "react",
            "authentication",
            "frontend",
            "backend",
            "server",
            "function",
            "class",
            "object",
            "machine learning"
        ]

        matched_keywords = 0

        for keyword in technical_keywords:

            if keyword in cleaned_answer:

                matched_keywords += 1

        # SCORING LOGIC

        if word_count <= 4:

            score = 1

            performance = "Needs Improvement"

            feedback = [

                "Answer is too short.",

                "Explain concepts properly.",

                "Add technical depth."
            ]

        elif matched_keywords == 0:

            score = 1

            performance = "Needs Improvement"

            feedback = [

                "Answer lacks technical relevance.",

                "Include actual technical concepts.",

                "Avoid vague or unrelated responses."
            ]

        elif matched_keywords <= 2:

            score = 4

            performance = "Average"

            feedback = [

                "Basic technical understanding detected.",

                "Add more technical depth.",

                "Use better explanations and examples."
            ]

        else:

            score = 8

            performance = "Excellent"

            feedback = [

                "Strong technical explanation.",

                "Good technical understanding.",

                "Well structured answer."
            ]

        return score, feedback, performance