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


def stats(data):
    return {
        "total_students": data["total_students"],
        "total_teachers": data["total_teachers"],
        "active_students_today": data["active_students_today"],
        }
    