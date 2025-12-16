# app/routes/routes.py

import math
import datetime
import random
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app import app, dao, login, db
from app.models import Course, Classroom, Enrollment, Bill, EnrollEnum, BillEnum, Employee

# --- IMPORT SERVICES MỚI ---
from app.services.email_service import EmailService
from app.services.payos_service import PayOSService




# ==========================================
# 1. TRANG CHỦ & LOAD KHÓA HỌC
# ==========================================
@app.route("/")
def index():
    kw = request.args.get('kw')
    age = request.args.get('age')
    page = request.args.get('page', 1, type=int)
    page_size = 6
    courses, total = dao.load_courses(kw=kw, page=page, page_size=page_size, age=age)
    total_pages = math.ceil(total / page_size)

    return render_template('layout/index.html',
                           courses=courses,
                           pages=total_pages,
                           current_page=page,
                           age_filter=age)


# ==========================================
# 2. LOGIN / LOGOUT / LOAD USER
# ==========================================
@login.user_loader
def load_user(user_id):
    return dao.get_user_by_id(user_id)


@app.route("/login", methods=['get', 'post'])
def login_process():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = dao.auth_user(username=username, password=password)
        if user:
            login_user(user)
            return redirect(request.args.get('next') or url_for('index'))
        else:
            return render_template('layout/login.html', err_msg="Tên đăng nhập hoặc mật khẩu không đúng!")
    return render_template('layout/login.html')


@app.route("/logout")
def logout_process():
    logout_user()
    return redirect(url_for('login_process'))


# ==========================================
# 3. ĐĂNG KÝ
# ==========================================
@app.route("/register", methods=['get', 'post'])
def register_process():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        password = request.form.get('password')
        confirm = request.form.get('confirm_password')

        if password == confirm:
            data = {
                'name': request.form.get('name'),
                'email': request.form.get('email'),
                'gender': request.form.get('gender'),
                'phone': request.form.get('phone'),
                'dob': request.form.get('dob'),
                'address': request.form.get('address'),
                'username': request.form.get('username'),
                'password': password,
                'avatar': request.form.get('avatar')
            }
            if dao.add_user(**data):
                flash('Đăng ký thành công! Vui lòng đăng nhập.', 'success')
                return redirect(url_for('login_process'))
            else:
                flash("Đăng ký thất bại! Username/Email/SĐT đã tồn tại.", 'danger')
        else:
            flash("Mật khẩu không khớp!", 'danger')
    return render_template('layout/register.html')


# ==========================================
# 4. PROFILE & CẬP NHẬT AVATAR
# ==========================================
@app.route("/profile")
@login_required
def student_profile():
    enrollment_info = dao.get_student_enrollment_info(current_user.id)
    return render_template('layout/profile.html', enrollment_info=enrollment_info)


@app.route("/profile/update_avatar", methods=['POST'])
@login_required
def update_avatar():
    new_avatar_url = request.form.get('new_avatar')
    if new_avatar_url and dao.update_user_avatar(current_user.id, new_avatar_url):
        flash('Cập nhật ảnh đại diện thành công!', 'success')
    else:
        flash('Lỗi khi cập nhật ảnh đại diện.', 'danger')
    return redirect(url_for('student_profile'))


# ---  ROUTE HỦY ĐĂNG KÝ ---
@app.route("/cancel-enrollment/<int:enrollment_id>", methods=['POST'])
@login_required
def cancel_enrollment(enrollment_id):
    if dao.delete_enrollment(enrollment_id):
        flash("Đã hủy đăng ký thành công!", "success")
    else:
        flash("Không thể hủy đăng ký này (Có thể do đã thanh toán hoặc lỗi hệ thống).", "danger")

    return redirect(url_for('student_profile'))


# ==========================================
# 5. CHI TIẾT KHÓA HỌC
# ==========================================
@app.route("/course/<course_id>")
def course_detail(course_id):
    course = Course.query.get_or_404(course_id)
    classes = sorted(course.classes, key=lambda x: x.start_date)
    return render_template('layout/course_detail.html', course=course, classes=classes)


# ==========================================
# 6. THANH TOÁN & PAYOS INTEGRATION
# ==========================================

@app.route("/checkout/<class_id>")
@login_required
def checkout(class_id):
    classroom = Classroom.query.get_or_404(class_id)
    existing_enrollment = Enrollment.query.filter_by(
        student_id=current_user.id,
        class_id=class_id
    ).first()

    # Nếu đã đăng ký, kiểm tra xem đã thanh toán chưa
    if existing_enrollment:
        bill = Bill.query.filter_by(enrollment_id=existing_enrollment.id).first()
        if bill and bill.status == BillEnum.PAID:
            flash("Bạn đã thanh toán khóa học này rồi!", "warning")
            return redirect(url_for('student_profile'))

    return render_template('layout/payment.html', classroom=classroom)


@app.route("/api/create-payment-link", methods=['POST'])
@login_required
def create_payment_link():
    data = request.json
    class_id = data.get('class_id')
    classroom = Classroom.query.get(class_id)

    if not classroom:
        return jsonify({'error': True, 'message': 'Lớp học không tồn tại'})

    try:
        cashiers = Employee.query.filter(Employee.id.startswith('102')).all()
        if cashiers:
            random_cashier = random.choice(cashiers)
            selected_cashier_id = random_cashier.id
        else:
            selected_cashier_id = '1020000003'

        # --- BƯỚC 1: TẠO DỮ LIỆU TRONG DB ---
        enrollment = Enrollment.query.filter_by(student_id=current_user.id, class_id=class_id).first()

        if not enrollment:
            enrollment = Enrollment(
                student_id=current_user.id,
                class_id=class_id,
                status=EnrollEnum.PENDING,
                register_date=datetime.date.today()
            )
            db.session.add(enrollment)
            db.session.flush()

        bill = Bill.query.filter_by(enrollment_id=enrollment.id).first()
        if not bill:
            bill = Bill(
                enrollment_id=enrollment.id,
                unit_price=classroom.course.fee,
                status=BillEnum.UNPAID,
                create_date=datetime.datetime.now(),
                cashier_id=selected_cashier_id
            )
            db.session.add(bill)
            db.session.commit()

        # --- BƯỚC 2: GỌI SERVICE ĐỂ TẠO LINK ---
        buyer_info = {
            "name": current_user.name,
            "email": current_user.email,
            "phone": current_user.phone_number
        }

        # Gọi PayOSService
        checkout_url = PayOSService.create_payment_link(
            bill_id=bill.id,
            amount=classroom.course.fee,
            course_name=classroom.name,
            buyer_info=buyer_info
        )

        return jsonify({
            'error': False,
            'checkoutUrl': checkout_url
        })

    except Exception as e:
        db.session.rollback()
        print(f"Lỗi thanh toán: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': True, 'message': str(e)})


@app.route("/payment-success")
def payment_success():
    flash("Thanh toán thành công! Khóa học đã được kích hoạt.", "success")
    return redirect(url_for('student_profile'))


@app.route("/payment-cancel")
def payment_cancel():
    flash("Giao dịch đã bị hủy.", "danger")
    return redirect(url_for('index'))


# ==========================================
#  (BACKDOOR TEST)
# ==========================================
@app.route("/test-payment-success/<int:enrollment_id>")
@login_required
def test_payment_success(enrollment_id):
    try:
        enrollment = Enrollment.query.get(enrollment_id)
        if not enrollment:
            flash("Không tìm thấy đăng ký này!", "danger")
            return redirect(url_for('student_profile'))

        bill = Bill.query.filter_by(enrollment_id=enrollment.id).first()

        # 1. Update DB
        if bill:
            bill.status = BillEnum.PAID

        enrollment.status = EnrollEnum.APPROVED
        db.session.commit()

        # 2. GỌI SERVICE GỬI MAIL (Code cũ phải gọi import lung tung, giờ gọn gàng)
        classroom = Classroom.query.get(enrollment.class_id)
        course = classroom.course

        # Gọi EmailService
        EmailService.send_enrollment_confirmation(current_user, course, classroom)

        flash(" (TEST) Đã kích hoạt khóa học và gửi mail thành công!", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"Lỗi khi test: {str(e)}", "danger")
        print(e)

    return redirect(url_for('student_profile'))