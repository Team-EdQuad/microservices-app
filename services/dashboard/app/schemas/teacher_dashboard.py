def individual_uploaded_assignment(assignment):
    return {
        "assignment_name": assignment["assignment_name"],
        "subject_name": assignment["subject_name"],
        "class_name": assignment["class_name"],
        "deadline": assignment["deadline"],
        "submission_count" : assignment["submission_count"],
        "total_students" : assignment["total_students"]
    }

def all_uploaded_assignments(assignments):
    return [individual_uploaded_assignment(assignment) for assignment in assignments]

def individual_progress(progress):
    return {
        "student_name": progress["student_name"],
        "first_term_avg": progress["first_term_avg"],
        "second_term_avg": progress["second_term_avg"],
        "third_term_avg": progress["third_term_avg"],
        "academic_attendance_rate": progress["academic_attendance_rate"],
        "non_academic_attendance_rate": progress["non_academic_attendance_rate"],
        "avg_academic_progress": progress["avg_academic_progress"]
    }

def all_progress(progresses):
    return [individual_progress(progress) for progress in progresses]