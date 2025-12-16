# app/services/payos_service.py

# Bỏ ItemData, CreatePaymentLinkRequest (*)
from payos import PayOS
from flask import url_for
import datetime

# Cấu hình PayOS
payos = PayOS(
    client_id="6034e4ba-0f39-486f-a024-e09f8768fc16",
    api_key="c2feb503-3f0d-4be7-afbe-25e852fb3741",
    checksum_key="17baf3da7ae973ddc2fab1864374c800869108488e1e835fd818a55c5d0f96d2"
)


class PayOSService:
    @staticmethod
    def create_payment_link(bill_id, amount, course_name, buyer_info):
        """
        Tạo link thanh toán PayOS
        """
        try:
            # Tạo mã đơn hàng
            order_code = int(bill_id) + int(datetime.datetime.now().timestamp())

            return_url = url_for('payment_success', _external=True)
            cancel_url = url_for('payment_cancel', _external=True)

            # Tạo danh sách sản phẩm (Dùng Dictionary thay vì ItemData)
            items = [{
                "name": f"Hoc phi {course_name}",
                "quantity": 1,
                "price": int(amount)
            }]

            payment_data = {
                "orderCode": order_code,
                "amount": int(amount),
                "description": f"Thanh toan Bill {bill_id}",
                "items": items,
                "returnUrl": return_url,
                "cancelUrl": cancel_url,
                "buyerName": buyer_info.get('name'),
                "buyerEmail": buyer_info.get('email'),
                "buyerPhone": buyer_info.get('phone') or "",
                "expiredAt": None
            }

            # Gọi API PayOS
            response = payos.payment_requests.create(payment_data)

            # Trả về link thanh toán
            return response.checkout_url

        except Exception as e:
            print(f" PayOSService Error: {str(e)}")
            raise e