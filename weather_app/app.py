from flask import Flask, render_template, request
import requests
from datetime import datetime

app = Flask(__name__)

API_KEY = "8e211d1ec08a99e281b338e8b79126be"

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
        hom_nay = datetime.now().strftime("%Y-%m-%d")
        ket_qua = []

        for muc in data["list"]:
            ngay_gio = muc["dt_txt"]
            if ngay_gio.startswith(hom_nay):
                ket_qua.append({
                    "gio": ngay_gio[11:16],
                    "nhiet_do": muc["main"]["temp"],
                    "mo_ta": muc["weather"][0]["description"].capitalize(),
                    "icon": muc["weather"][0]["icon"]
                })
        return ket_qua
    except:
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    du_bao_ngay = du_bao_gio = None
    thanh_pho = ""
    don_vi = "metric"

    if request.method == 'POST':
        thanh_pho = request.form.get('city')
        don_vi = request.form.get('don_vi', 'metric')
        du_bao_ngay = lay_du_bao_5_ngay(thanh_pho, API_KEY, don_vi)
        du_bao_gio = lay_du_bao_theo_gio(thanh_pho, API_KEY, don_vi)

    return render_template("index.html",
                           du_bao_ngay=du_bao_ngay,
                           du_bao_gio=du_bao_gio,
                           thanh_pho=thanh_pho,
                           don_vi=don_vi)

if __name__ == '__main__':
    app.run(debug=True)
