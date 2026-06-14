def detect_role(text):

    text = text.lower()

    if (
        "figma" in text or
        "ui" in text or
        "ux" in text or
        "design" in text
    ):

        return "UI/UX Designer"

    elif (
        "flask" in text or
        "django" in text or
        "api" in text or
        "backend" in text
    ):

        return "Backend Developer"

    elif (
        "react" in text or
        "javascript" in text or
        "frontend" in text
    ):

        return "Frontend Developer"

    elif (
        "machine learning" in text or
        "tensorflow" in text or
        "pandas" in text
    ):

        return "ML Engineer"

    return "Software Developer"