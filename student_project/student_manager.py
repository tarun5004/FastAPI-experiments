import json
from typing import List, Optional

class Student:
    """Student class - oop concept"""
    def __init__(self, id: int, name: str, age: int, grade: str, subjects: List[str]):
        self.id = id
        self.name = name
        self.age = age
        self.grade = grade
        self.subjects = subjects
        
    def to_dict(self):
        # why we convert to dict? because json can't serialize custom objects directly  
        #convert object to dictionary
        
        return{
            "id": self.id,
            "name": self.name,
            "age": self.age,
            "grade": self.grade,
            "subjects": self.subjects
        }
        
        
class StudentManager:
    """Manager class to handle student database operations"""
    
    def __init__(self, filepath: str = "students.json"):  #default filepath
        self.filepath = filepath
        
    def load_students(self) -> List[Student]:
        """Load all students from the JSON file"""
        try:
            with open(self.filepath, 'r') as f:
                data = json.load(f)
            return data['students']
        except FileNotFoundError:
            # If file not found, return empty list
            print(f"Error:{self.filepath} not found. Returning empty list.")
            return []
        except json.JSONDecodeError:
            # If JSON is invalid
            print(f"Error: Invalid JSON format in {self.filepath}")
            return []
        except KeyError:
            # 'students' key not found in JSON data
            print(f"Error: 'students' key not found in JSON data")
            return []
        except Exception as e:
            #any other error
            print(f"An unexpected error occurred: {e}")
            return []
        
        
    def save_students(self, students: List[dict]) -> bool:
        """Save students to JSON file"""
        try:
            with open(self.filepath, 'w') as f:
                json.dump({"students": students}, f, indent=2)
            return True
        except IOError as e:
            print(f"Error: Cannot write to file {self.filepath}: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error while saving students: {e}")
            return False
        
        
    def get_all(self) -> List[dict]: #define get_all method to return all students as list of dictionaries
        return self.load_students()
    
    def get_by_id(self, student_id: int) -> Optional[dict]:
        """get student by id - using list comprehension"""
        
        try:
            students = self.load_students()
            result = [s for s in students if s['id'] == student_id]  
            return result[0] if result else None
        except Exception as e:
            print(f"Error in get_by_id: {e}")
            return None
        
    def filter_by_grade(self, grade: str) -> List[dict]:
        """Filter students by grade"""
        try:
            students = self.load_students()
            return [s for s in students if s['grade'] == grade]
        except Exception as e:
            print(f"Error in filter by grade: {e}")
            return []
        
    def filter_by_age(self, min_age: int, max_age: int = None) -> List[dict]:
        """Filter students by age range - comprehension with conditions"""
        try:
            students = self.load_students()
            if max_age:
                return [s for s in students if min_age <= s['age'] <= max_age] # both min and max age provided (why we use this condition? to avoid error when max_age is None)
            return [s for s in students if s['age']>= min_age]  # only min_age provided
        except Exception as e:
            print(f"Error in filter by age: {e}")
            return []
            
    def add_students(self, student_data: dict) -> Optional[dict]:
        """Add new student - Python basics: max(), list operations"""
        try:
            # validate required fields
            required_fields = ['name', 'age', 'grade', 'subjects']
            for field in required_fields:
                if field not in student_data:
                    raise ValueError(f"Missing required field: {field}")
                
            students = self.load_students()
            # Generate new ID using max() and list comprehension
            new_id = max([s['id'] for s in students]) + 1 if students else 1 # if no students, start with ID 1 mean empty list
            student_data['id'] = new_id
            students.append(student_data)
            
            if self.save_students(students):
                return student_data
            return None
        except ValueError as e:
            print(f"Validation error: {e}")
            return None
        except Exception as e:
            print(f"Error adding new student: {e}")
            return None
        
    def update_student(self, student_id: int, updated_data: dict) -> Optional[dict]:
        """Update existing student - dict operations"""
        try:
            students = self.load_students()
            # Find and update using enumerate
            for i, student in enumerate(students):
                if student['id'] == student_id:
                    # Update only provided fields (dict merge)
                    students[i].update(updated_data)
                    students[i]['id'] = student_id  # Keep original ID
                    
                    if self.save_students(students):
                        return students[i]
                    return None
            # Student not found
            print(f"Student with ID {student_id} not found")
            return None
        except Exception as e:
            print(f"Error in update_student: {e}")
            return None    
    
    
    def delete_student(self, student_id: int) -> bool:
        """Delete student - list filtering"""
        try:
            students = self.load_students()
            # Filter out the student using list comprehension
            filtered_student = [s for s in students if s['id'] != student_id]
            
            if len(filtered_student) < len(students):  
                return self.save_students(filtered_student)
            print(f"Student with ID {student_id} not found")
            return False
        except Exception as e:
            print(f"Error in delete_student: {e}")
            return False
    
    
    def get_statistics(self) -> dict:
        """Get stats - comprehensions + dict operations"""
        try:
            students = self.load_students()
            
            if not students:
                return {
                    "total_students": 0,
                    "average_age": 0,
                    "grade_distribution": {},
                    "unique_subjects": []
                }
                
            # Dict comprehension for grade count
            grade_count = {}
            for s in students:
                grade = s['grade']
                grade_count[grade] = grade_count.get(grade, 0) +1
                
            # Average age using sum() and len()
            avg_age = sum([s['age'] for s in students]) / len(students)
            
            # All unique subjects using set comprehension
            all_subjects = {subject for s in students for subject in s['subjects']}
            
            return {
                "total_students": len(students),
                "average_age": round(avg_age, 2),
                "grade_distribution": grade_count,
                "unique_subjects": sorted(list(all_subjects))
            }
        except Exception as e:
            print(f"Error in get_statistics: {e}")
            return {
                "total_students": 0,
                "average_age": 0,
                "grade_distribution": {},
                "unique_subjects": []
            }