import re


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

    section_map = {
        "strengths": "strengths",
        "strength": "strengths",
        "missing skills": "missing_skills",
        "missing skill": "missing_skills",
        "skill gaps": "missing_skills",
        "skill gap": "missing_skills",
        "resume improvements": "improvements",
        "resume improvement": "improvements",
        "improvements": "improvements",
        "improvement": "improvements",
        "ats recommendations": "ats_recommendations",
        "ats recommendation": "ats_recommendations",
        "recommendations": "ats_recommendations",
        "recommendation": "ats_recommendations",
        "summary": "summary"
    }

    lines = feedback.splitlines()

    current_section = None

    for line in lines:

        line = line.strip()

        if not line:
            continue

        cleaned_heading = re.sub(
            r"^[#*\-\s]+|[#*\-\s]+$",
            "",
            line
        )

        cleaned_heading = re.sub(
            r":\s*$",
            "",
            cleaned_heading
        )

        heading_key = cleaned_heading.lower().strip()

        if heading_key in section_map:

            current_section = section_map[heading_key]

            continue

        if not current_section:
            continue

        cleaned_line = line

        cleaned_line = re.sub(
            r"^\s*[-*•]\s*",
            "",
            cleaned_line
        )

        cleaned_line = re.sub(
            r"^\s*\d+\s*[\.\)]\s*",
            "",
            cleaned_line
        )

        cleaned_line = re.sub(
            r"^\s*[-*•]\s*\d+\s*[\.\)]\s*",
            "",
            cleaned_line
        )

        cleaned_line = re.sub(
            r"\*\*(.*?)\*\*",
            r"\1",
            cleaned_line
        )

        cleaned_line = re.sub(
            r"\*(.*?)\*",
            r"\1",
            cleaned_line
        )

        cleaned_line = re.sub(
            r"`(.*?)`",
            r"\1",
            cleaned_line
        )

        cleaned_line = re.sub(
            r"\s+",
            " ",
            cleaned_line
        ).strip()

        if not cleaned_line:
            continue

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

    for key in [
        "strengths",
        "missing_skills",
        "improvements",
        "ats_recommendations"
    ]:

        sections[key] = sections[key][:5]

    if not sections["summary"]:

        if sections["missing_skills"]:

            sections["summary"] = (
                "Your resume has relevant strengths, "
                "but addressing the identified skill gaps "
                "and ATS recommendations can improve "
                "your alignment with this role."
            )

        elif sections["strengths"]:

            sections["summary"] = (
                "Your resume shows good alignment with "
                "the selected role. Strengthening the "
                "recommended areas can further improve "
                "your ATS compatibility."
            )

        elif sections["improvements"]:

            sections["summary"] = (
                "Your resume has opportunities for "
                "improvement. Applying the recommendations "
                "can make it clearer, more relevant, "
                "and ATS-friendly."
            )

        else:

            sections["summary"] = (
                "Review the analysis results and "
                "recommendations to improve your resume "
                "for the selected role."
            )

    if not any([
        sections["strengths"],
        sections["missing_skills"],
        sections["improvements"],
        sections["ats_recommendations"]
    ]):

        sections["improvements"] = [
            "The AI response could not be structured. "
            "Please run the analysis again."
        ]

    return sections