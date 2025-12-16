from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail

app = Flask(__name__)

# --- CẤU HÌNH CƠ BẢN ---
app.secret_key = '08032005' #(?)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:08032005@localhost/engdb?charset=utf8mb4'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

# --- CẤU HÌNH EMAIL  ---
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True

# 1. Điền email
app.config['MAIL_USERNAME'] = 'dephucau@gmail.com'

# 2. Điền mật khẩu ứng dụng
app.config['MAIL_PASSWORD'] = 'bgax buho jptr hgle'

# Tên hiển thị khi người dùng nhận được mail
app.config['MAIL_DEFAULT_SENDER'] = ('ENGLISH CENTER', 'dephucau@gmail.com')

db = SQLAlchemy(app=app)
login = LoginManager(app)

login.login_view = 'login_process'
login.login_message = "Vui lòng đăng nhập để sử dụng chức năng này!"
login.login_message_category = "danger"

# Khởi tạo Mail
mail = Mail(app)

# Import routes sau khi app đã khởi tạo xong
from app.routes import routes