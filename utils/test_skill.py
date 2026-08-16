from skill_matcher import compare_skills

resume = """
Python
Flask
SQL
MySQL
Git
Pandas
"""

job = """
Python
Flask
SQL
MySQL
Docker
AWS
Git
"""

result = compare_skills(resume, job)

print("Resume Skills:", result["resume_skills"])
print("Job Skills:", result["job_skills"])
print("Matched Skills:", result["matched_skills"])
print("Missing Skills:", result["missing_skills"])
print("Match Percentage:", result["match_percentage"])