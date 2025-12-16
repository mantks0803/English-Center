# app/dao.py

from app.models import User, Student, Course, AgeEnum, Classroom, Enrollment, Bill, EnrollEnum, BillEnum, Employee
from app import db
import hashlib
import random
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_


def get_user_by_id(user_id):
    return User.query.get(user_id)


def auth_user(username, password):
    password = password.strip()
    user = User.query.filter(User.username == username.strip()).first()

    if not user:
        return None

    input_password_hash = str(hashlib.md5(password.encode('utf-8')).hexdigest())

    # Trường hợp 1: Mật khẩu khớp mã Hash
    #Do database tự tạo data mật khẩu :123, khi tạo user mới sẽ tạo mk mã hóa
    if user.password == input_password_hash:
        return user

    # Trường hợp 2: Mật khẩu khớp text thường (User cũ) -> Tự động cập nhật hash
    if user.password == password:
        try:
            user.password = input_password_hash
            db.session.commit()
        except Exception as ex:
            print(f"Lỗi tự động update password hash: {ex}")
        return user

    return None


def add_user(name, email, gender, phone, dob, address, username, password, avatar=None):
    suffix = str(random.randint(0, 9999999)).zfill(7)
    gen_id = f"103{suffix}"
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())

    if not avatar:
        avatar = f"https://ui-avatars.com/api/?name={name}&background=0D8ABC&color=fff&size=128"

    try:
        u = Student(id=gen_id, name=name, email=email, gender=int(gender),
                    phone_number=phone, dob=dob, address=address,
                    avatar=avatar, username=username, password=password, type='student')
        db.session.add(u)
        db.session.commit()
        return True
    except IntegrityError as ex:
        db.session.rollback()
        print(f"Lỗi Integrity: {ex}")
        return False
    except Exception as ex:
        db.session.rollback()
        print(f"Lỗi chung: {ex}")
        return False


def load_courses(kw=None, page=1, page_size=6, age=None):
    query = Course.query

    if kw:
        if kw == 'chung-chi':
            query = query.filter(or_(Course.name.contains('IELTS'), Course.name.contains('TOEIC')))
        else:
            query = query.filter(Course.name.contains(kw))

    if age:
        if age == '1':
            query = query.filter(Course.age == AgeEnum.KIDS)
        elif age == '2':
            query = query.filter(Course.age == AgeEnum.TEEN)
        elif age == '3':
            query = query.filter(Course.age == AgeEnum.ADULT)

    total = query.count()

    start = (page - 1) * page_size
    courses = query.offset(start).limit(page_size).all()

    return courses, total


def get_student_enrollment_info(student_id):
    """
    Lấy danh sách lớp học của học viên kèm trạng thái đóng tiền, mã khóa học và tên giáo viên
    """
    query = db.session.query(
        Enrollment.id.label('enrollment_id'),
        Enrollment.status.label('enrollment_status'),
        Enrollment.register_date,
        Classroom.id.label('class_id'),
        Classroom.name.label('class_name'),
        Classroom.start_date,
        Course.id.label('course_id'),
        Course.name.label('course_name'),
        Course.image.label('course_image'),
        Course.fee,
        Bill.status.label('bill_status'),
        Employee.name.label('teacher_name')
    ).join(Classroom, Enrollment.class_id == Classroom.id) \
        .join(Course, Classroom.course_id == Course.id) \
        .outerjoin(Employee, Classroom.teacher_id == Employee.id) \
        .outerjoin(Bill, Bill.enrollment_id == Enrollment.id) \
        .filter(Enrollment.student_id == student_id) \
        .order_by(Enrollment.register_date.desc()) \
        .all()

    return query


def update_user_avatar(user_id, new_avatar_url):
    try:
        user = User.query.get(user_id)
        if user:
            user.avatar = new_avatar_url
            db.session.commit()
            return True
        return False
    except Exception as ex:
        print(f"Lỗi cập nhật avatar: {ex}")
        db.session.rollback()
        return False

# --- HÀM XÓA ĐĂNG KÝ ---
def delete_enrollment(enrollment_id):
    try:
        # 1. Tìm Enrollment
        enrollment = Enrollment.query.get(enrollment_id)
        if not enrollment:
            return False

        # 2. Tìm Bill tương ứng và xóa trước (để tránh lỗi khóa ngoại)
        bill = Bill.query.filter_by(enrollment_id=enrollment_id).first()
        if bill:
            if bill.status == BillEnum.PAID:  # Nếu lỡ đóng tiền rồi thì không cho xóa kiểu này
                return False
            db.session.delete(bill)

        # 3. Xóa Enrollment
        db.session.delete(enrollment)
        db.session.commit()
        return True
    except Exception as ex:
        db.session.rollback()
        print(f"Lỗi xóa đăng ký: {ex}")
        return False


def get_student_by_id(student_id):

    return Student.query.get(student_id)


def get_cashier_bills(cashier_id):

    return db.session.query(
        Bill.id.label('bill_id'),
        Bill.status.label('bill_status'),
        Bill.create_date,
        Bill.unit_price,
        Student.name.label('student_name'),
        Student.id.label('student_id'),
        Course.name.label('course_name'),
        Classroom.name.label('class_name')
    ).join(Enrollment, Bill.enrollment_id == Enrollment.id) \
        .join(Student, Enrollment.student_id == Student.id) \
        .join(Classroom, Enrollment.class_id == Classroom.id) \
        .join(Course, Classroom.course_id == Course.id) \
        .filter(Bill.cashier_id == cashier_id) \
        .order_by(Bill.create_date.desc()) \
        .all()
