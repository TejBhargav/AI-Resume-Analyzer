def parse_ai_feedback(feedback):

    sections = {
        "summary": "",
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

        if lower_line == "summary":
            current_section = "summary"
            continue

        if lower_line == "strengths":
            current_section = "strengths"
            continue

        if (
            lower_line == "missing skills"
            or lower_line == "skill gaps"
        ):
            current_section = "missing_skills"
            continue

        if (
            lower_line == "resume improvements"
            or lower_line == "improvements"
        ):
            current_section = "improvements"
            continue

        if (
            lower_line == "ats recommendations"
            or lower_line == "recommendations"
        ):
            current_section = "ats_recommendations"
            continue

        if current_section:

            cleaned_line = line

            if cleaned_line.startswith("-"):
                cleaned_line = cleaned_line[1:].strip()

            elif cleaned_line.startswith("*"):
                cleaned_line = cleaned_line[1:].strip()

            elif (
                len(cleaned_line) >= 2
                and cleaned_line[0].isdigit()
                and cleaned_line[1] in [".", ")"]
            ):
                cleaned_line = cleaned_line[2:].strip()

            elif (
                len(cleaned_line) >= 3
                and cleaned_line[0].isdigit()
                and cleaned_line[1].isdigit()
                and cleaned_line[2] in [".", ")"]
            ):
                cleaned_line = cleaned_line[3:].strip()

            if cleaned_line:

                if current_section == "summary":

                    if sections["summary"]:
                        sections["summary"] += " " + cleaned_line
                    else:
                        sections["summary"] = cleaned_line

                else:

                    if cleaned_line not in sections[current_section]:
                        sections[current_section].append(
                            cleaned_line
                        )

    if not sections["summary"]:

        if sections["strengths"]:
            sections["summary"] = (
                "Your resume shows relevant strengths for the selected "
                "role. Review the skill gaps and recommended improvements "
                "to further improve your ATS compatibility."
            )

    if not any([
        sections["strengths"],
        sections["missing_skills"],
        sections["improvements"],
        sections["ats_recommendations"]
    ]):

        sections["improvements"] = [
            feedback
        ]

    return sections