from flask import Flask, render_template, request, jsonify, redirect, url_for
import requests
from datetime import datetime, timedelta
from pytz import timezone
import pytz

app = Flask(__name__)

API_KEY = "8e211d1ec08a99e281b338e8b79126be"

@app.route("/suggest_city")
def suggest_city():
    query = request.args.get("query", "")
    if not query:
        return jsonify([])

    url = f"http://api.openweathermap.org/geo/1.0/direct?q={query}&limit=5&appid={API_KEY}"
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        data = res.json()

        results = []
        for item in data:
            name = item.get("name")
            state = item.get("state", "")
            country = item.get("country", "")
            description = name
            if state:
                description += f", {state}"
            if country:
                description += f", {country}"

            results.append({
                "name": name,
                "description": description,
                "lat": item.get("lat"),
                "lon": item.get("lon")
            })

        return jsonify(results)
    except Exception as e:
        print("Lỗi tìm kiếm gợi ý thành phố:", e)
        return jsonify([])

# @app.route("/search_city")
# def search_city():
#     keyword = request.args.get("q", "")
#     if not keyword:
#         return jsonify([])

#     url = f"http://api.openweathermap.org/geo/1.0/direct?q={keyword}&limit=5&appid={API_KEY}"
#     try:
#         res = requests.get(url, timeout=10)
#         res.raise_for_status()
#         data = res.json()

#         results = []
#         for item in data:
#             name = item.get("name")
#             state = item.get("state", "")
#             country = item.get("country", "")
#             # Tạo chuỗi mô tả (có state hoặc không)
#             description = name
#             if state:
#                 description += f", {state}"
#             if country:
#                 description += f", {country}"

#             results.append({
#                 "name": name,
#                 "description": description,
#                 "lat": item.get("lat"),
#                 "lon": item.get("lon")
#             })

#         return jsonify(results)
#     except Exception as e:
#         print("Lỗi tìm kiếm thành phố:", e)
#         return jsonify([])


@app.route("/weather_by_location", methods=["POST"])
def weather_by_location():
    data = request.get_json()
    lat = data.get("lat")
    lon = data.get("lon")

    if not lat or not lon:
        return jsonify({"error": "Thiếu tọa độ."}), 400

    # Gọi API reverse geocoding để lấy tên thành phố từ tọa độ
    geo_url = f"http://api.openweathermap.org/geo/1.0/reverse?lat={lat}&lon={lon}&limit=1&appid={API_KEY}"
    try:
        res = requests.get(geo_url, timeout=10)
        res.raise_for_status()
        data = res.json()

        if data and len(data) > 0:
            city_name = data[0].get("name")
            return redirect(url_for("index", city=city_name))
        else:
            return jsonify({"error": "Không thể xác định tên thành phố."}), 400
    except:
        return jsonify({"error": "Lỗi kết nối đến OpenWeatherMap."}), 500


@app.template_filter('datetimeformat')
def datetimeformat(value, format='%d/%m/%Y'):
    try:
        dt = datetime.strptime(value, '%Y-%m-%d')
        return dt.strftime(format)
    except Exception:
        return value

def lay_du_bao_5_ngay(thanh_pho, api_key, units):
    url = f"https://api.openweathermap.org/data/2.5/forecast?q={thanh_pho}&appid={api_key}&units={units}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        du_bao = data['list']

        ket_qua = {}
        for muc in du_bao:
            ngay_gio = muc['dt_txt']
            ngay = ngay_gio.split(' ')[0]
            gio = ngay_gio.split(' ')[1]
            if gio == "12:00:00" and ngay not in ket_qua:
                ket_qua[ngay] = {
                    'nhiet_do': muc['main']['temp'],
                    'mo_ta': muc['weather'][0]['description'].capitalize(),
                    'icon': muc['weather'][0]['icon']
                }
        return ket_qua
    except:
        return None

def lay_du_bao_theo_gio(thanh_pho, api_key, units):
    url = f"https://api.openweathermap.org/data/2.5/forecast?q={thanh_pho}&appid={api_key}&units={units}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        ket_qua = []

        tz_vn = timezone('Asia/Ho_Chi_Minh')
        now_vn = datetime.now(tz_vn).date()

        for muc in data["list"]:
            dt_utc = datetime.strptime(muc["dt_txt"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=pytz.utc)
            dt_vn = dt_utc.astimezone(tz_vn)
            if dt_vn.date() == now_vn:
                ket_qua.append({
                    "gio": dt_vn.strftime("%H:%M"),
                    "gio_full": dt_vn.strftime("%H:%M, %d/%m/%Y"),
                    "nhiet_do": muc["main"]["temp"],
                    "mo_ta": muc["weather"][0]["description"].capitalize(),
                    "icon": muc["weather"][0]["icon"]
                })
        return ket_qua
    except Exception as e:
        print("Lỗi lấy dự báo theo giờ:", e)
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    du_bao_ngay = du_bao_gio = None
    don_vi = "metric"
    thanh_pho = ""

    if request.method == 'POST':
        thanh_pho = request.form.get('city')
        don_vi = request.form.get('don_vi', 'metric')
    else:
        thanh_pho = request.args.get('city', '')

    if thanh_pho:
        du_bao_ngay = lay_du_bao_5_ngay(thanh_pho, API_KEY, don_vi)
        du_bao_gio = lay_du_bao_theo_gio(thanh_pho, API_KEY, don_vi)
        if du_bao_gio:
            for muc in du_bao_gio:
                muc['gio_full'] = muc['gio']

    # Lấy giờ hiện tại theo múi giờ VN
    tz_vn = timezone('Asia/Ho_Chi_Minh')
    gio_hien_tai = datetime.now(tz_vn).strftime("%H:%M")

    return render_template("index.html",
                           du_bao_ngay=du_bao_ngay,
                           du_bao_gio=du_bao_gio,
                           thanh_pho=thanh_pho,
                           don_vi=don_vi,
                           gio_hien_tai=gio_hien_tai)


if __name__ == '__main__':
    app.run(debug=True)