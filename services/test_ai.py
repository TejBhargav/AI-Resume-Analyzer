import sys
import os

sys.path.insert(
    0,
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from services.ai import generate_ai_feedback


resume = """
Python developer with experience in Python, Flask, MySQL,
SQL, Git and GitHub. Developed web applications using Flask.
"""

job = """
We are looking for a Python Developer with experience in
Python, Flask, MySQL, SQL, Docker, AWS and Git.
"""


result = generate_ai_feedback(
    resume,
    job
)


print()
print("=" * 60)
print("AI RESUME ANALYSIS")
print("=" * 60)
print()
print(result)
print()
print("=" * 60)