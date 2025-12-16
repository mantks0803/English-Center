# app/services/email_service.py
from threading import Thread
from flask_mail import Message
from flask import render_template
from app import app, mail


class EmailService:
    @staticmethod
    def _send_async(app, msg):
        """Hàm chạy ngầm"""
        with app.app_context():
            try:
                mail.send(msg)
                print("EmailService: Đã gửi mail thành công!")
            except Exception as e:
                print(f" EmailService Error: {str(e)}")

    @staticmethod
    def send_enrollment_confirmation(user, course, classroom):
        """
        Gửi mail xác nhận đăng ký khóa học
        """
        subject = f"Xác nhận đăng ký thành công: {course.name}"

        # Render nội dung HTML
        html_body = render_template(
            'email/confirmation.html',
            user=user,
            course=course,
            classroom=classroom
        )

        msg = Message(subject, recipients=[user.email], html=html_body)

        # Chạy luồng riêng
        thr = Thread(target=EmailService._send_async, args=(app, msg))
        thr.start()