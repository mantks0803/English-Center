document.addEventListener("DOMContentLoaded", function() {

    // ==========================================
    // 1. HEADER STICKY LOGIC
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
            if (window.scrollY > 50) {
                header.classList.add('scrolled');
            } else {
                header.classList.remove('scrolled');
            }
        });
    }

    // ==========================================
    // 2. MODAL THÔNG BÁO (login.html)
    // ==========================================
    const modalElement = document.getElementById('notificationModal');
    if (modalElement) {
        var myModal = new bootstrap.Modal(modalElement);
        myModal.show();
    }

    // ==========================================
    // 3. SMOOTH SCROLL (index.html & header contact)
    // ==========================================
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.has('page') || urlParams.has('kw') || urlParams.has('age')) {
        const target = document.getElementById('target-scroll-position');
        if (target) {
            setTimeout(() => {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }, 150);
        }
    }

    // ==========================================
    // 4. CLOUDINARY WIDGET (profile.html & register.html)
    // ==========================================
    const uploadBtn = document.getElementById("upload_widget");

    if (uploadBtn) {
        // Cấu hình Cloudinary
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

                // 1. Cập nhật ảnh Preview
                const previewImg = document.getElementById("avatarPreview");
                if (previewImg) previewImg.src = imageUrl;

                // 2. Điền URL vào input ẩn (cho Register)
                const avatarInput = document.getElementById("avatarInput");
                if (avatarInput) avatarInput.value = imageUrl;

                // 3. Điền URL vào input ẩn (cho Profile Update)
                const newAvatarInput = document.getElementById("newAvatarInput");
                if (newAvatarInput) newAvatarInput.value = imageUrl;

                // 4. Nếu là trang Profile -> Tự động submit form
                const updateForm = document.getElementById("avatarUpdateForm");
                if (updateForm) {
                    updateForm.submit();
                }
            }
        });

        uploadBtn.addEventListener("click", function(){
            myWidget.open();
        }, false);
    }

    // ==========================================
    // 5. COURSE DETAIL LOGIC (course_detail.html)
    // ==========================================
    const classRadios = document.querySelectorAll('.class-selector');
    if (classRadios.length > 0) {
        const detailContainer = document.getElementById('class-details-container');
        const placeholder = document.getElementById('class-detail-placeholder');

        const detailName = document.getElementById('detail_name');
        const detailId = document.getElementById('detail_id');
        const detailDatesDisplay = document.getElementById('detail_dates_display');
        const detailTeacher = document.getElementById('detail_teacher');
        const detailSlots = document.getElementById('detail_slots');
        const detailSchedule = document.getElementById('detail_schedule');
        const btnRegister = document.getElementById('btnRegister');

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

            if(btnRegister) btnRegister.disabled = false;
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

        // Tự động chọn lớp đầu tiên nếu có
        if(classRadios.length > 0) {
             classRadios[0].checked = true;
             updateClassDetails(classRadios[0]);
             classRadios[0].closest('.list-group-item').classList.add('active');
        }
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
    // 7. PAYMENT PROCESS LOGIC -FINAL (12)
    // ==========================================
    const btnPayment = document.getElementById('btn-process-payment');

    if (btnPayment) {
        btnPayment.addEventListener('click', function() {
            // 1. Disable nút để tránh click nhiều lần
            this.disabled = true;
            this.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i> ĐANG XỬ LÝ...';

            const classId = this.getAttribute('data-class-id');

            // 2. Gọi API tạo link thanh toán (Fetch API)
            fetch('/api/create-payment-link', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ class_id: classId })
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert('Lỗi: ' + data.message);
                    // Reset nút
                    btnPayment.disabled = false;
                    btnPayment.innerHTML = '<i class="fas fa-lock me-2"></i> THANH TOÁN NGAY';
                } else {
                    // 3. Chuyển hướng sang trang thanh toán của PayOS
                    window.location.href = data.checkoutUrl;
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Có lỗi xảy ra khi kết nối server.');
                btnPayment.disabled = false;
                btnPayment.innerHTML = '<i class="fas fa-lock me-2"></i> THANH TOÁN NGAY';
            });
        });
    }

});