import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Date, Enum, ForeignKey, Time, Boolean
from sqlalchemy.dialects.mysql import DECIMAL, DOUBLE
from sqlalchemy.dialects.mssql import TINYINT
from app import app, db
from flask_login import UserMixin



# 1. CẤP ĐỘ 1: USER


# Thêm UserMixin vào class User
class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id = Column(String(10), primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(100), nullable=False)
    gender = Column(Integer, nullable=False, default=0)  # 0 = nữ, 1 = nam
    phone_number = Column(String(10), unique=True)
    dob = Column(Date, nullable=False)
    address = Column(String(250))
    avatar = Column(String(500),
                    default="https://res.cloudinary.com/du9oap5y2/image/upload/v1764921187/user_icon_izjcfk.png",
                    server_default="https://res.cloudinary.com/du9oap5y2/image/upload/v1764921187/user_icon_izjcfk.png")
    username = Column(String(30), nullable=False, unique=True)
    password = Column(String(50), nullable=False)
    status = Column(TINYINT, default=1)  # 1: Active, 0: Inactive

    type = Column(String(20))

    __mapper_args__ = {
        'polymorphic_identity': 'user',
        'polymorphic_on': type
    }


    # Nếu status = 1 (Active) thì cho đăng nhập, ngược lại chặn.
    @property
    def is_active(self):
        return self.status == 1



# 2. CẤP ĐỘ 2: NHÁNH HỌC VIÊN & NHÂN VIÊN

class Student(User):
    id = Column(String(10), ForeignKey('user.id'), primary_key=True)

    emergency_contact = Column(String(250))
    # occupation = Column(String(150))
    # source_channel = Column(String(100))  # Nguồn khách (Facebook, Google...) (?)

    __mapper_args__ = {
        'polymorphic_identity': 'student'
    }


# --- B. EMPLOYEE (Lớp trung gian Nhân viên) ---
class Employee(User):
    id = Column(String(10), ForeignKey('user.id'), primary_key=True)

    salary = Column(DECIMAL(10, 2), nullable=False, default=0)
    hired_date = Column(Date, default=datetime.now)

    __mapper_args__ = {
        'polymorphic_identity': 'employee'
    }



# 3. CẤP ĐỘ 3: NHÂN VIÊN CỤ THỂ


class Teacher(Employee):
    id = Column(String(10), ForeignKey('employee.id'), primary_key=True)

    major = Column(String(100))
    degree = Column(String(100))

    __mapper_args__ = {
        'polymorphic_identity': 'teacher'
    }


class Cashier(Employee):
    id = Column(String(10), ForeignKey('employee.id'), primary_key=True)

    shift = Column(String(50))

    __mapper_args__ = {
        'polymorphic_identity': 'cashier'
    }


class Admin(Employee):
    id = Column(String(10), ForeignKey('employee.id'), primary_key=True)

    access_level = Column(Integer, default=0)  # 0: Chủ, 1: Quản lý
    # digital_signature = Column(String(255))  # Ảnh chữ ký số (để ký báo cáo)
    report_email = Column(String(100))  # Email nhận báo cáo tự động

    __mapper_args__ = {
        'polymorphic_identity': 'admin'
    }



# 4. CÁC ENUM & MODEL NGHIỆP VỤ


class AgeEnum(enum.Enum):
    KIDS = 0
    TEEN = 1
    ADULT = 2


class SkillEnum(enum.Enum):
    BEGINNER = 0
    INTERMEDIATE = 1
    ADVANCED = 2


class DayOfWeek(enum.Enum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6


class EnrollEnum(enum.Enum):
    PENDING = 0
    APPROVED = 1
    REJECTED = 2


class BillEnum(enum.Enum):
    UNPAID = 0
    PAID = 1


class AttendanceStatusEnum(enum.Enum):
    PRESENT = 0
    ABSENT = 1


class Course(db.Model):
    id = Column(String(10), primary_key=True)
    name = Column(String(100), nullable=False)
    fee = Column(DECIMAL(10, 2), nullable=False)
    age = Column(Enum(AgeEnum), nullable=False)
    level = Column(Enum(SkillEnum), nullable=False)
    duration_hour = Column(String(10), nullable=False)
    course_description = Column(String(250))
    image = Column(String(500))


class Classroom(db.Model):
    id = Column(String(10), primary_key=True)
    name = Column(String(100), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    max_student = Column(Integer, nullable=False)

    teacher_id = Column(String(10), ForeignKey('teacher.id'), nullable=False)
    course_id = Column(String(10), ForeignKey(Course.id), nullable=False)

    course = db.relationship('Course', backref='classes')
    teacher = db.relationship('Teacher', backref='teaching_classes')

    @property
    def schedules_display(self):

        if not self.schedules:
            return "Chưa có lịch"

        data_map = {
            "MONDAY": '2', "TUESDAY": '3', "WEDNESDAY": '4',
            "THURSDAY": '5', "FRIDAY": '6', "SATURDAY": '7', "SUNDAY": 'CN'}

        data_sort = sorted(self.schedules, key=lambda s: s.day.value)
        day_vn = []
        for s in data_sort:
            day_en = s.day.name
            day_vn.append(data_map[day_en])

        day_vn = list(dict.fromkeys(day_vn))

        time_display = self.schedules[0].start_time.strftime(' (%H:%M)') if self.schedules else ""
        return "Thứ " + " - ".join(day_vn) + time_display


class ScheduleDetail(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    day = Column(Enum(DayOfWeek), nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)

    class_id = Column(String(10), ForeignKey(Classroom.id), nullable=False)
    classroom = db.relationship('Classroom', backref='schedules')


class GradeComponent(db.Model):
    __tablename__ = 'grade_component'
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(50), nullable=False)
    weight = Column(DOUBLE, nullable=False)

    course_id = Column(String(10), ForeignKey(Course.id), nullable=False)
    course = db.relationship('Course', backref='grade_components')


class Enrollment(db.Model):
    id = Column(Integer, autoincrement=True, primary_key=True)
    register_date = Column(Date, nullable=False, default=datetime.now)
    status = Column(Enum(EnrollEnum), nullable=False)

    student_id = Column(String(10), ForeignKey('student.id'), nullable=False)
    class_id = Column(String(10), ForeignKey(Classroom.id), nullable=False)

    student = db.relationship('Student', backref='enrollments')
    classroom = db.relationship('Classroom', backref='enrollments')


class Attendance(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False, default=datetime.now)
    status = Column(Enum(AttendanceStatusEnum), nullable=False, default=AttendanceStatusEnum.PRESENT)
    note = Column(String(250))

    enrollment_id = Column(Integer, ForeignKey(Enrollment.id), nullable=False)
    enrollment = db.relationship('Enrollment', backref='attendances')


class Score(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    score = Column(DOUBLE, nullable=False)

    enrollment_id = Column(Integer, ForeignKey(Enrollment.id), nullable=False)
    grade_id = Column(Integer, ForeignKey(GradeComponent.id), nullable=False)

    enrollment = db.relationship('Enrollment', backref='scores')
    grade_component = db.relationship('GradeComponent', backref='scores')


class Bill(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    create_date = Column(DateTime, nullable=False, default=datetime.now)
    status = Column(Enum(BillEnum), nullable=False)
    unit_price = Column(DECIMAL(10, 2), nullable=False)

    enrollment_id = Column(Integer, ForeignKey(Enrollment.id), nullable=False)

    cashier_id = Column(String(10), ForeignKey('cashier.id'), nullable=False)

    enrollment = db.relationship('Enrollment', backref='bills')
    cashier = db.relationship('Cashier', backref='processed_bills')
