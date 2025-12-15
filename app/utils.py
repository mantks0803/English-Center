# app/utils.py
from threading import Thread
from flask_mail import Message
from flask import render_template
from app import app, mail


def send_async_email(app, msg):
    """
    Hàm chạy ngầm trong luồng riêng (Worker)
    """
    with app.app_context():
        try:
            mail.send(msg)
            print(" Gửi mail thành công!")
        except Exception as e:
            print(f" Lỗi gửi mail: {str(e)}")


def send_enrollment_confirmation_email(user, course, classroom):
    """
    API nội bộ: Gửi mail xác nhận đăng ký khóa học
    """
    subject = f"Xác nhận đăng ký thành công: {course.name}"

    # Render nội dung HTML từ template
    html_body = render_template(
        'email/confirmation.html',
        user=user,
        course=course,
        classroom=classroom
    )

    msg = Message(subject, recipients=[user.email], html=html_body)

    # Tạo luồng riêng để gửi mail
    thr = Thread(target=send_async_email, args=(app, msg))
    thr.start()