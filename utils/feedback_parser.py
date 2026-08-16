def parse_ai_feedback(feedback):

    sections = {
        "strengths": [],
        "missing_skills": [],
        "improvements": [],
        "ats_recommendations": []
    }

    if not feedback:
        return sections

    lines = feedback.splitlines()

    current_section = None

    for line in lines:

        line = line.strip()

        if not line:
            continue

        lower_line = line.lower()

        if "strength" in lower_line:
            current_section = "strengths"
            continue

        if (
            "missing skill" in lower_line
            or "skill gap" in lower_line
        ):
            current_section = "missing_skills"
            continue

        if (
            "improvement" in lower_line
            or "resume improvement" in lower_line
        ):
            current_section = "improvements"
            continue

        if (
            "ats recommendation" in lower_line
            or "ats recommendation" in lower_line
            or "recommendation" in lower_line
        ):
            current_section = "ats_recommendations"
            continue

        if current_section:

            cleaned_line = line

            if cleaned_line.startswith("-"):
                cleaned_line = cleaned_line[1:].strip()

            elif cleaned_line.startswith("*"):
                cleaned_line = cleaned_line[1:].strip()

            elif cleaned_line[:2].isdigit():
                cleaned_line = cleaned_line[2:].strip()

            if cleaned_line:
                sections[current_section].append(
                    cleaned_line
                )

    if not any(sections.values()):

        sections["improvements"] = [
            feedback
        ]

    return sections