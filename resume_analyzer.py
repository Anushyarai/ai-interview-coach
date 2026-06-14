def analyze_resume(text, skills):

    strengths = []

    weaknesses = []

    suggestions = []

    score = 0

    # SKILL ANALYSIS
    if len(skills) >= 5:

        strengths.append("Good technical skill diversity.")
        score += 3

    else:

        weaknesses.append("Add more technical skills.")
        suggestions.append("Include more relevant technologies and tools.")

    # PROJECT CHECK
    if "project" in text.lower():

        strengths.append("Projects section detected.")
        score += 2

    else:

        weaknesses.append("Projects section missing.")
        suggestions.append("Add strong technical projects.")

    # EDUCATION CHECK
    if "education" in text.lower():

        strengths.append("Education details included.")
        score += 2

    else:

        weaknesses.append("Education section missing.")

    # EXPERIENCE CHECK
    if "experience" in text.lower():

        strengths.append("Experience section detected.")
        score += 2

    else:

        weaknesses.append("No experience section found.")
        suggestions.append("Add internships or practical experience.")

    # ATS SCORE
    if score >= 8:

        overall = "Excellent Resume"

    elif score >= 5:

        overall = "Good Resume"

    else:

        overall = "Needs Improvement"

    return {
        "strengths": strengths,
        "weaknesses": weaknesses,
        "suggestions": suggestions,
        "score": score,
        "overall": overall
    }