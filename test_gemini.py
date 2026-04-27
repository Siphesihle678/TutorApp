import os
from dotenv import load_dotenv

# Load the environment variables from .env
load_dotenv()

from app.services.ai_service import ai_assistant

test_content = """
Microsoft Access is a Database Management System (DBMS) from Microsoft that combines the relational Microsoft Jet Database Engine with a graphical user interface and software-development tools.
It is a member of the Microsoft 365 suite of applications, included in the Professional and higher editions or sold separately.
Microsoft Access stores data in its own format based on the Access Jet Database Engine.
"""

print("Generating quiz from content...")
result = ai_assistant.generate_quiz_from_content(test_content)
import json
print(json.dumps(result, indent=2))
