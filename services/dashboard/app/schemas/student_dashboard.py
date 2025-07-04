def inidividual_progress(progress):
    return {
        "subject_id": progress["subject_id"],
        "class_id": progress["class_id"],
        "subject_name": progress["subject_name"],
        "total_content": progress["total_content"],
        "completed_content": progress["completed_content"],
        "progress_percentage": progress["progress_percentage"]
    }

def all_progress(progresses):
    return [inidividual_progress(progress) for progress in progresses]


def individual_assignment(assignment):
    return {
        "assignment_id": assignment["assignment_id"],
        "assignment_name": assignment["assignment_name"],
        "subject_name": assignment["subject_name"],
        "class_id": assignment["class_id"],
        "deadline": assignment["deadline"],
        "status": assignment["status"]
    }

def all_assignments(assignments):
    return [individual_assignment(assignment) for assignment in assignments]

def academic_attendance_rate(attendance):
    return {
        "total_days": attendance["total_days"],
        "days_present": attendance["days_present"],
        "attendance_rate": attendance["attendance_rate"]
    }

def monthly_attendance_rate(attendance):
    return {
        "month": attendance["month"],
        "attendance_rate": attendance["attendance_rate"]
    }