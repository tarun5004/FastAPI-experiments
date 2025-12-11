from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from student_manager import StudentManager

# creating FastAPI instance

app = FastAPI(
    title="Student Management API",
    description="A simple API to manage students - learning project",
    version="1.0.0"
)

# student manager instance
manager = StudentManager("students.json") # why we import filepath here? to specify the json file location mean we can change it if needed


# ==========================================
# PYDANTIC MODELS (Data Validation)
# ==========================================

class studentCreate(BaseModel):
    """Model for creating a new student"""
    name: str
    age: int
    grade: str
    subjects: List[str]
    
class studentUpdate(BaseModel):
    """Model for updating student - all fields optional"""
    name: Optional[str]  = None
    age: Optional[int] = None
    grade: Optional[str] = None
    subjects: Optional[List[str]] = None
    #why we use Optional here? because when updating, not all fields are required
    
# ==========================================
# API ENDPOINTS
# ==========================================

# 1. HOME - GET /
@app.get("/")
def home():
    """Welcome endpoint""" 
    return {
        "message": "Welcome to the Student Management API!",
        "version": "1.0.0",
        "endpoints": {
            "all_students": "/students",
            "single_student": "/students/{id}",
            "search": "/students/search?name=xyz",
            "filter_by_grade": "/students/filter/grade/{grade}",
            "statistics": "/students/starts"
        }
    }
    
# 2. GET /students - get all students
@app.get("/students")
def get_all_students():
    """Get all students"""
    students = manager.get_all()  # why we use manager.get_all()? to call the method from student_manager.py
    return {
        "total": len(students), # total number of students
        "students": students    # list of students
    }
    
# 3. GET /students/{id} - get student by ID
@app.get("/students/{student_id}")
def get_student_by_id(student_id: int):
    """Get single student by ID - using path parameter"""
    student = manager.get_by_id(student_id) # call get_by_id method from student_manager.py
    
    if not student:
        raise HTTPException(status_code=404, detail="Student with ID {student_id} not found")
    
    return student


# 4. Search students by name - GET /students/search?name=xyz
@app.get("/students/search")
def search_students(name: str):
    """Search students by name - using query parameter"""
    results = manager.search_by_name(name) # call search_by_name method from student_manager.py
    return {
        "search_query": name,
        "found": len(results),
        "students": results
    }
    
# 5. FILTER BY GRADE - GET /students/filter/grade/{grade}
@app.get("/students/filter/grade/{grade}")
def filter_by_grade(grade: str):
    """Filter students by grade - Path Parameter"""
    results = manager.filter_by_grade(grade)
    return {
        "grade": grade,
        "found": len(results),
        "students": results
    }


# 6. FILTER BY AGE - GET /students/filter/age?min=18&max=25
@app.get("/students/filter/age/")
def filter_by_age(min_age: int, max_age: Optional[int] = None):
    """Filter by age range - Query Parameters"""
    results = manager.filter_by_age(min_age, max_age)
    return {
        "min_age": min_age,
        "max_age": max_age,
        "found": len(results),
        "students": results
    }
    
# 7. GET STATISTICS - GET /students/stats
@app.get("/students/stats")         #what is this endpoint for? to get statistics about students meaning total number of students, average age, grade distribution, unique subjects
def get_statistics():
    """Get student statistics"""
    return manager.get_statistics()  # call get_statistics method from student_manager.py

# 8. ADD NEW STUDENT - POST /students
@app.post("/students")
def add_student(student: studentCreate): # create new student using pydantic model
    """Add new student - Post with request body"""
    student_data = student.model_dump() # convert pydantic model to dict mean we can use it in student_manager.py
    result = manager.add_students(student_data) # call add_students method from student_manager.py
    
    if not result:
        raise HTTPException(status_code=500, detail="Failed to add new student")
    return {
        "message" : "Student added successfully",
        "student" : result
    }
    
# 9. UPDATE STUDENT - PUT /students/{id}
@app.put("/students/{student_id}")
def update_student(student_id: int, student: studentUpdate): 
    """Update existing student - PUT with path parameter and request body"""
    #only fields provided in the request body will be updated
    update_data = {k: v for k, v in student.model_dump().items() if v is not None} # explain this line? we create a dict comprehension to filter out None values from the pydantic model like if name is None, it will not be included in updated_data
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No data provided for update")
    
    result = manager.update_student(student_id, update_data) # call update_student method from student_manager.py
    
    if not result:
        raise HTTPException(status_code=404, detail=f"Student with ID {student_id} not found or update failed")
    
    return {
        "message": "Student updated successfully",
        "student": result
    }
    
# 10. DELETE STUDENT - DELETE /students/{id}
@app.delete("/students/{student_id}")
def delete_student(student_id: int):
    """Delete student - DELETE with path parameter"""
    success = manager.delete_student(student_id) # call delete_student method from student_manager.py
    
    if not success:
        raise HTTPException(status_code=404, detail=f"Student with ID {student_id} not found or deletion failed")
    
    return {
        "message": "Student deleted successfully"
    }