document.addEventListener("DOMContentLoaded", function() {

    // ==========================================
    // 1. HEADER STICKY
    // ==========================================
    const header = document.querySelector('.main-header');
    if (header) {
        function updateHeaderHeight() {
            const height = header.offsetHeight;
            document.body.style.setProperty("--header-height", height + "px");
            document.body.classList.add("has-fixed-header");
        }
        window.addEventListener('load', updateHeaderHeight);
        window.addEventListener('resize', updateHeaderHeight);
        window.addEventListener('scroll', () => {
            if (window.scrollY > 50) header.classList.add('scrolled');
            else header.classList.remove('scrolled');
        });
    }

    // ==========================================
    // 2. MODAL THÔNG BÁO
    // ==========================================
    const modalElement = document.getElementById('notificationModal');
    if (modalElement) {
        var myModal = new bootstrap.Modal(modalElement);
        myModal.show();
    }

    // ==========================================
    // 3. SMOOTH SCROLL
    // ==========================================
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.has('page') || urlParams.has('kw') || urlParams.has('age')) {
        const target = document.getElementById('target-scroll-position');
        if (target) {
            setTimeout(() => {
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }, 150);
        }
    }

    // ==========================================
    // 4. CLOUDINARY WIDGET
    // ==========================================
    const uploadBtn = document.getElementById("upload_widget");
    if (uploadBtn) {
        var myWidget = cloudinary.createUploadWidget({
            cloudName: 'dmhnfoc9i',
            uploadPreset: 'ml_default',
            sources: ['local', 'url', 'camera'],
            multiple: false,
            cropping: true,
            croppingAspectRatio: 1,
            showSkipCropButton: false,
            folder: 'english-center-avatars'
        }, (error, result) => {
            if (!error && result && result.event === "success") {
                var imageUrl = result.info.secure_url;
                const previewImg = document.getElementById("avatarPreview");
                if (previewImg) previewImg.src = imageUrl;

                const avatarInput = document.getElementById("avatarInput");
                if (avatarInput) avatarInput.value = imageUrl;

                const newAvatarInput = document.getElementById("newAvatarInput");
                if (newAvatarInput) newAvatarInput.value = imageUrl;

                const updateForm = document.getElementById("avatarUpdateForm");
                if (updateForm) updateForm.submit();
            }
        });
        uploadBtn.addEventListener("click", function(){ myWidget.open(); }, false);
    }

    // ==========================================
    // 5. LOGIC TRANG CHI TIẾT KHÓA HỌC
    // ==========================================
    const classRadios = document.querySelectorAll('.class-selector');
    const btnRegister = document.getElementById('btnRegister');

    if (classRadios.length > 0) {
        const detailContainer = document.getElementById('class-details-container');
        const placeholder = document.getElementById('class-detail-placeholder');

        const detailName = document.getElementById('detail_name');
        const detailId = document.getElementById('detail_id');
        const detailDatesDisplay = document.getElementById('detail_dates_display');
        const detailTeacher = document.getElementById('detail_teacher');
        const detailSlots = document.getElementById('detail_slots');
        const detailSchedule = document.getElementById('detail_schedule');

        function updateClassDetails(radio) {
            if(placeholder) placeholder.style.display = 'none';
            if(detailContainer) detailContainer.style.display = 'block';

            const name = radio.getAttribute('data-name');
            const id = radio.getAttribute('data-id');
            const start = radio.getAttribute('data-start');
            const end = radio.getAttribute('data-end');
            const teacher = radio.getAttribute('data-teacher');
            const slots = radio.getAttribute('data-students');
            const schedule = radio.getAttribute('data-schedule');

            if(detailName) detailName.innerText = name;
            if(detailId) detailId.innerText = id;
            if(detailDatesDisplay) detailDatesDisplay.innerHTML = `<span class="text-dark">Từ: ${start}</span> - <span class="text-dark">Đến: ${end}</span>`;
            if(detailTeacher) detailTeacher.innerText = teacher;
            if(detailSlots) detailSlots.innerText = slots;
            if(detailSchedule) detailSchedule.innerText = schedule;

            if(btnRegister) {
                btnRegister.disabled = false;
                if (btnRegister.tagName === 'A') {
                    btnRegister.setAttribute('href', "/pos/create-invoice/" + id);
                }
            }
        }

        classRadios.forEach(radio => {
            radio.addEventListener('change', function() {
                if (this.checked) {
                    updateClassDetails(this);
                    document.querySelectorAll('.list-group-item').forEach(item => item.classList.remove('active'));
                    this.closest('.list-group-item').classList.add('active');
                }
            });
            radio.closest('label').addEventListener('click', function(e) {
                if (e.target.tagName !== 'INPUT') {
                    const inputRadio = this.querySelector('.class-selector');
                    if (!inputRadio.checked) {
                        inputRadio.checked = true;
                        updateClassDetails(inputRadio);
                        document.querySelectorAll('.list-group-item').forEach(item => item.classList.remove('active'));
                        this.classList.add('active');
                    }
                }
            });
        });

        if(classRadios.length > 0) {
             classRadios[0].checked = true;
             updateClassDetails(classRadios[0]);
             classRadios[0].closest('.list-group-item').classList.add('active');
        }
    }

    if(btnRegister && btnRegister.tagName === 'BUTTON') {
        btnRegister.addEventListener('click', function() {
            const selectedRadio = document.querySelector('input[name="selected_class"]:checked');
            if (selectedRadio) {
                window.location.href = "/checkout/" + selectedRadio.value;
            } else {
                alert("Vui lòng chọn một lớp học!");
            }
        });
    }

    // ==========================================
    // 6. HEADER INTRO
    // ==========================================
    const introTriggers = document.querySelectorAll('.intro-modal-trigger');
    const introModalElement = document.getElementById('introModal');
    if (introTriggers.length > 0 && introModalElement) {
        const introModal = new bootstrap.Modal(introModalElement);
        const modalTitle = document.getElementById('introModalLabel');
        const modalImg = document.getElementById('introModalImg');
        const modalContent = document.getElementById('introModalContent');

        introTriggers.forEach(trigger => {
            trigger.addEventListener('click', function(e) {
                e.preventDefault();
                const title = this.getAttribute('data-title');
                const img = this.getAttribute('data-img');
                const content = this.getAttribute('data-content');
                if(modalTitle) modalTitle.textContent = title;
                if(modalImg) modalImg.src = img;
                if(modalContent) modalContent.textContent = content;
                introModal.show();
            });
        });
    }

    // ==========================================
    // 7. XỬ LÝ THANH TOÁN QR (Trang payment.html)
    // ==========================================
    const btnPayment = document.getElementById('btn-process-payment');
    if (btnPayment) {
        btnPayment.addEventListener('click', function() {
            this.disabled = true;
            this.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i> ĐANG XỬ LÝ...';
            const classId = this.getAttribute('data-class-id');

            fetch('/api/create-payment-link', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ class_id: classId })
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert('Lỗi: ' + data.message);
                    btnPayment.disabled = false;
                    btnPayment.innerHTML = '<i class="fas fa-lock me-2"></i> THANH TOÁN NGAY';
                } else {
                    window.location.href = data.checkoutUrl;
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Mất kết nối server.');
                btnPayment.disabled = false;
                btnPayment.innerHTML = '<i class="fas fa-lock me-2"></i> THANH TOÁN NGAY';
            });
        });
    }

    // ==========================================
    // 8. LOGIC THu ngân
    // ==========================================

    // a. Tìm kiếm học viên
    const studentIdInput = document.getElementById('studentIdInput');
    if (studentIdInput) {
        studentIdInput.addEventListener('change', function() {
            let studentId = this.value;
            if(studentId.length > 3) {
                fetch('/api/student-info/' + studentId)
                    .then(response => response.json())
                    .then(data => {
                        const nameDisplay = document.getElementById('studentNameDisplay');
                        const nameInput = document.getElementById('studentNameInput');

                        if (data.found) {
                            if(nameInput) nameInput.value = data.name;
                            if(nameDisplay) nameDisplay.innerHTML = '<i class="fas fa-check-circle"></i> Tìm thấy: ' + data.name;
                        } else {
                            if(nameInput) nameInput.value = '';
                            if(nameDisplay) nameDisplay.innerHTML = '<i class="fas fa-exclamation-triangle text-danger"></i> Không tìm thấy ID này!';
                        }
                    });
            }
        });
    }

    // b. Đổi nút bấm khi chọn Tiền mặt / QR
    const paymentMethodSelect = document.getElementById('paymentMethodSelect');
    const cashBtns = document.getElementById('cashButtons');
    const qrBtns = document.getElementById('qrButtons');

    function toggleButtons() {
        if (!paymentMethodSelect) return;

        if (paymentMethodSelect.value === 'CASH') {
            if(cashBtns) cashBtns.style.display = 'grid';
            if(qrBtns) qrBtns.style.display = 'none';
        } else {
            if(cashBtns) cashBtns.style.display = 'none';
            if(qrBtns) qrBtns.style.display = 'grid';
        }
    }

    if (paymentMethodSelect) {
        toggleButtons();
        paymentMethodSelect.addEventListener('change', toggleButtons);
    }

    // c. XỬ LÝ FORM HÓA ĐƠN
    const invoiceForm = document.getElementById('invoiceForm');
    if (invoiceForm) {
        invoiceForm.addEventListener('submit', function(e) {
            // Lấy cái nút mà người dùng vừa bấm (submitter)
            const btnClicked = e.submitter;
            const currentMethod = document.getElementById('paymentMethodSelect').value;

            // TRƯỜNG HỢP 1: Bấm nút QR nhưng đang chọn Tiền mặt -> CHẶN
            if (btnClicked && btnClicked.value === 'QR' && currentMethod === 'CASH') {
                e.preventDefault();
                alert("Phương thức thanh toán không hợp lệ! (Bạn đang chọn Tiền mặt)");
                return;
            }

            // TRƯỜNG HỢP 2: Bấm nút Lưu Tiền mặt (hoặc Lưu & Xuất) -> HỎI XÁC NHẬN
            if (btnClicked && (btnClicked.value === 'CASH' || btnClicked.value === 'CASH_EXPORT')) {
                // Hiện popup xác nhận
                let confirmAction = confirm("Xác nhận đã thu đủ tiền và muốn lưu hóa đơn?");

                if (!confirmAction) {
                    // Nếu chọn Cancel -> Dừng lại, không gửi form
                    e.preventDefault();
                }
                // Nếu chọn OK -> Form tự động gửi đi (Server xử lý tiếp)
            }
        });
    }

    // ==========================================
    // 9. AUTO PRINT PDF
    // ==========================================
    const invoiceTemplate = document.getElementById('invoiceTemplate');
    if (invoiceTemplate) {
        const filename = invoiceTemplate.getAttribute('data-filename');
        const redirectUrl = invoiceTemplate.getAttribute('data-redirect-url');

        invoiceTemplate.style.display = 'block';

        var opt = {
            margin:       10,
            filename:     filename,
            image:        { type: 'jpeg', quality: 0.98 },
            html2canvas:  { scale: 2 },
            jsPDF:        { unit: 'mm', format: 'a4', orientation: 'portrait' }
        };

        html2pdf().from(invoiceTemplate).set(opt).save().then(function(){
            invoiceTemplate.style.display = 'none';
            alert("Đã xuất hóa đơn PDF thành công!");
            setTimeout(function(){
                window.location.href = redirectUrl;
            }, 1000);
        });
    }

});