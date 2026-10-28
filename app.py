
from flask import Flask, request, jsonify, send_from_directory
import requests
import os

app = Flask(__name__, static_folder=".")


@app.get("/")
def home():
    return send_from_directory(".", "index.html")


@app.get("/api/stats")
def stats():
    url = request.args.get("url", "").strip()

    if not url.startswith((
        "https://www.tiktok.com/",
        "https://m.tiktok.com/",
        "https://vm.tiktok.com/",
        "https://vt.tiktok.com/"
    )):
        return jsonify(
            error="Link TikTok không hợp lệ hoặc không được hỗ trợ."
        ), 400

    try:
        response = requests.get(
            "https://www.tikwm.com/api/",
            params={"url": url},
            headers={
                "User-Agent": "Mozilla/5.0",
                "Accept": "application/json"
            },
            timeout=25
        )

        app.logger.info(
            "TikWM HTTP status=%s; response=%s",
            response.status_code,
            response.text[:500]
        )

        response.raise_for_status()
        data = response.json()

        if data.get("code") not in (None, 0, "0"):
            return jsonify(
                error=data.get("msg")
                or "Dịch vụ dữ liệu không trả về video."
            ), 502

        return jsonify(data)

    except requests.Timeout:
        app.logger.exception("TikWM request timeout")
        return jsonify(
            error="Dịch vụ lấy số liệu hết thời gian chờ. Thử lại sau."
        ), 504

    except requests.RequestException:
        app.logger.exception("Loi khi goi dich vu TikWM")
        return jsonify(
            error="Không kết nối được dịch vụ dữ liệu TikTok. Vui lòng thử lại."
        ), 502

    except ValueError:
        app.logger.exception("TikWM tra ve JSON khong hop le")
        return jsonify(
            error="Dịch vụ dữ liệu trả về phản hồi không hợp lệ."
        ), 502


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=False)
