def detect_weak_topics(question, score):

    weak_topics = []

    if score <= 4:

        question = question.lower()

        if "api" in question:

            weak_topics.append("APIs")

        if "database" in question:

            weak_topics.append("Databases")

        if "authentication" in question:

            weak_topics.append("Authentication")

        if "react" in question:

            weak_topics.append("React")

    return weak_topics