
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

# uri = "mongodb+srv://user:1234@cluster0.tcrks.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
uri = "mongodb+srv://admin:1234@cluster0.ogyx0.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# db = client.nonacademic
db  = client.LMS
collection31 = db["sports"]
collection32 = db["clubs"]

student_table = db["student"]
content_table = db["content"]
subject_table= db["subject"]
student_content_table = db["student_content"]
assignment_table = db["assignment"]
submission_table = db["submission"] 
# academic_attendance_table = db["academic_attendance"]
academic_attendance_table = db["attendance_store"]
non_academic_attendance_table = db["non_academic_attendance"]
exam_table = db["exam_marks"]

behavioural_table = db["behavioral_analysis"]

class_table = db["class"]
teacher_table = db["teacher"]
admin_table = db["admin"]

admin_table = db["admin"]
student_login_table = db["student_login_details"]





