import random
import string
from sqlalchemy.orm import Session
from ..models.user import User

def generate_tutor_code(length: int = 6) -> str:
    """Generate a random tutor code with letters and numbers"""
    # Use uppercase letters and numbers
    characters = string.ascii_uppercase + string.digits
    # Exclude similar looking characters (0, O, 1, I, L)
    characters = characters.replace('0', '').replace('O', '').replace('1', '').replace('I', '').replace('L', '')
    
    while True:
        code = ''.join(random.choice(characters) for _ in range(length))
        # Ensure it starts with a letter
        if code[0].isalpha():
            return code

def generate_unique_tutor_code(db: Session, length: int = 6) -> str:
    """Generate a unique tutor code that doesn't exist in the database"""
    max_attempts = 100
    attempts = 0
    
    while attempts < max_attempts:
        code = generate_tutor_code(length)
        
        # Check if code already exists
        existing_user = db.query(User).filter(User.tutor_code == code).first()
        if not existing_user:
            return code
        
        attempts += 1
    
    # If we can't find a unique code with 6 characters, try with more
    return generate_unique_tutor_code(db, length + 1)

def find_tutor_by_code(db: Session, tutor_code: str) -> User:
    """Find a tutor by their tutor code"""
    return db.query(User).filter(
        User.tutor_code == tutor_code,
        User.role == "teacher",
        User.is_active == True
    ).first()

