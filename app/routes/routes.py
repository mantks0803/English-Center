# app/routes/routes.py

import math
import datetime
import random
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app import app, dao, login, db
from app.models import Course, Classroom, Enrollment, Bill, EnrollEnum, BillEnum, Employee

# --- May cai service tu viet ---
from app.services.email_service import EmailService
from app.services.payos_service import PayOSService
# --- Import json ---
import json


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
# 3. ĐĂNG KÝ TÀI KHOẢN
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
                flash("Đăng ký thất bại! Username hoặc Email đã tồn tại.", 'danger')
        else:
            flash("Mật khẩu xác nhận không khớp!", 'danger')
    return render_template('layout/register.html')


# ==========================================
# 4. PROFILE & CẬP NHẬT AVATAR
# ==========================================
@app.route("/profile")
@login_required
def student_profile():
    # Phân biệt Thu ngân (102) và Học viên
    if current_user.id.startswith('102'):
        data = dao.get_cashier_bills(current_user.id)
    else:
        data = dao.get_student_enrollment_info(current_user.id)

    return render_template('layout/profile.html', enrollment_info=data)


@app.route("/profile/update_avatar", methods=['POST'])
@login_required
def update_avatar():
    new_avatar_url = request.form.get('new_avatar')
    if new_avatar_url and dao.update_user_avatar(current_user.id, new_avatar_url):
        flash('Cập nhật ảnh đại diện thành công!', 'success')
    else:
        flash('Lỗi! Không thể thay đổi ảnh đại diện.', 'danger')
    return redirect(url_for('student_profile'))


# ---  HỦY ĐĂNG KÝ ---
@app.route("/cancel-enrollment/<int:enrollment_id>", methods=['POST'])
@login_required
def cancel_enrollment(enrollment_id):
    if dao.delete_enrollment(enrollment_id):
        flash("Hủy đăng ký khóa học thành công!", "success")
    else:
        flash("Không thể hủy! Khóa học đã đóng tiền hoặc có lỗi hệ thống.", "danger")

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
# 6. THANH TOÁN & PAYOS
# ==========================================

@app.route("/checkout/<class_id>")
@login_required
def checkout(class_id):
    classroom = Classroom.query.get_or_404(class_id)
    existing_enrollment = Enrollment.query.filter_by(
        student_id=current_user.id,
        class_id=class_id
    ).first()

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

        # --- TẠO DATA TRONG DB ---
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

        # --- GỌI SERVICE PAYOS ---
        buyer_info = {
            "name": current_user.name,
            "email": current_user.email,
            "phone": current_user.phone_number
        }

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

        # 1. Update DB thanh PAID
        if bill:
            bill.status = BillEnum.PAID

        enrollment.status = EnrollEnum.APPROVED
        db.session.commit()

        # 2. Gọi hàm gửi mail
        classroom = Classroom.query.get(enrollment.class_id)
        course = classroom.course

        EmailService.send_enrollment_confirmation(current_user, course, classroom)

        flash(" Thanh toán thành công và đã gửi mail!", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"Lỗi khi test: {str(e)}", "danger")
        print(e)

    return redirect(url_for('student_profile'))


# ==========================================
# API CHECK HỌC VIÊN
# ==========================================
@app.route('/api/student-info/<student_id>')
@login_required
def get_student_info(student_id):
    student = dao.get_student_by_id(student_id)
    if student:
        return jsonify({'found': True, 'name': student.name})
    return jsonify({'found': False})


# ==========================================
# KHU VỰC THU NGÂN
# ==========================================

@app.route("/pos/create-invoice/<class_id>", methods=['GET', 'POST'])
@login_required
def pos_create_invoice(class_id):
    # Check quyen thu ngan
    if not current_user.id.startswith('102'):
        flash("Bạn không có quyền truy cập trang này!", "danger")
        return redirect(url_for('index'))

    classroom = Classroom.query.get_or_404(class_id)

    # Bien nay de chua du lieu hoa don khi can xuat PDF
    new_bill_data = None

    if request.method == 'POST':
        action = request.form.get('action')
        student_id = request.form.get('student_id')

        # Check ma hoc vien
        student = dao.get_student_by_id(student_id)
        if not student:
            flash("Mã Học Viên không chính xác!", "danger")
            return redirect(url_for('pos_create_invoice', class_id=class_id))

        try:
            # 1. Tao Enrollment
            is_cash_payment = (action == 'CASH' or action == 'CASH_EXPORT')

            enroll_status = EnrollEnum.APPROVED if is_cash_payment else EnrollEnum.PENDING
            enrollment = Enrollment(
                student_id=student_id,
                class_id=class_id,
                status=enroll_status,
                register_date=datetime.date.today()
            )
            db.session.add(enrollment)
            db.session.flush()

            # 2. Tao Bill
            bill_status = BillEnum.PAID if is_cash_payment else BillEnum.UNPAID
            bill = Bill(
                enrollment_id=enrollment.id,
                unit_price=classroom.course.fee,
                status=bill_status,
                create_date=datetime.datetime.now(),
                cashier_id=current_user.id
            )
            db.session.add(bill)
            db.session.commit()

            # 3. Xu ly sau khi luu DB

            # --- TRUONG HOP: TIEN MAT (Luu thuong) ---
            if action == 'CASH':
                EmailService.send_enrollment_confirmation(student, classroom.course, classroom)
                flash(f"Thu tiền mặt thành công! (Mã hóa đơn #{bill.id})", "success")
                return redirect(url_for('student_profile'))

            # --- TRUONG HOP: TIEN MAT (Luu & Xuat PDF) ---
            elif action == 'CASH_EXPORT':
                EmailService.send_enrollment_confirmation(student, classroom.course, classroom)
                flash("Đã lưu hóa đơn! Hệ thống đang xuất file PDF...", "success")

                # Tao du lieu de render ra mau hoa don
                new_bill_data = {
                    "id": bill.id,
                    "student_name": student.name,
                    "student_id": student.id,
                    "course_name": classroom.course.name,
                    "class_name": classroom.name,
                    "cashier_name": current_user.name,
                    "date": bill.create_date.strftime("%d/%m/%Y %H:%M"),
                    "amount": "{:,.0f}".format(classroom.course.fee)
                }
                # Render lai chinh trang nay kem theo du lieu hoa don de JS chup hinh
                return render_template('layout/pos_invoice.html', classroom=classroom, new_bill_data=new_bill_data)

            # --- TRUONG HOP: QR CODE ---
            elif action == 'QR':
                buyer_info = {"name": student.name, "email": student.email, "phone": student.phone_number}
                checkout_url = PayOSService.create_payment_link(
                    bill_id=bill.id,
                    amount=classroom.course.fee,
                    course_name=classroom.name,
                    buyer_info=buyer_info
                )
                return redirect(checkout_url)

        except Exception as e:
            db.session.rollback()
            flash(f"Đã xảy ra lỗi trong quá trình xử lý: {str(e)}", "danger")

    return render_template('layout/pos_invoice.html', classroom=classroom, new_bill_data=new_bill_data)


# --- IN LAI HOA DON CU (REPRINT) ---
@app.route("/pos/reprint-invoice/<int:bill_id>")
@login_required
def reprint_invoice(bill_id):
    # Chi thu ngan moi duoc in lai
    if not current_user.id.startswith('102'):
        flash("Bạn không có quyền thực hiện chức năng này!", "danger")
        return redirect(url_for('index'))

    # Tim hoa don trong DB
    bill = Bill.query.get_or_404(bill_id)

    # Lay thong tin lien quan (hoc vien, lop, khoa hoc) qua cac bang lien ket
    enrollment = bill.enrollment
    classroom = enrollment.classroom
    student = enrollment.student

    # Check xem hoa don nay da thanh toan chua (chi in hoa don PAID)
    if bill.status != BillEnum.PAID:
        flash("Hóa đơn này chưa thanh toán, không thể in!", "warning")
        return redirect(url_for('student_profile'))

    # Chuan bi du lieu de in (Giong het luc tao moi)
    reprint_data = {
        "id": bill.id,
        "student_name": student.name,
        "student_id": student.id,
        "course_name": classroom.course.name,
        "class_name": classroom.name,
        "cashier_name": current_user.name,  # Nguoi in la nguoi dang dang nhap
        "date": bill.create_date.strftime("%d/%m/%Y %H:%M"),  # Ngay gio cua hoa don cu
        "amount": "{:,.0f}".format(bill.unit_price)
    }

    flash("In hóa đơn thành công!", "info")

    # Render ra cai trang pos_invoice nhung kem bien new_bill_data de no tu dong in
    return render_template('layout/pos_invoice.html', classroom=classroom, new_bill_data=reprint_data)