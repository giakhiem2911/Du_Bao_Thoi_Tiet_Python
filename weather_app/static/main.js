const toggleBtn = document.getElementById('toggleTheme');
const htmlTag = document.documentElement;

toggleBtn.addEventListener('click', () => {
    const currentTheme = htmlTag.getAttribute('data-bs-theme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    htmlTag.setAttribute('data-bs-theme', newTheme);
    toggleBtn.innerHTML = newTheme === 'dark' ?
        '<i class="bi bi-brightness-high"></i> Light Mode' :
        '<i class="bi bi-moon-stars"></i> Dark Mode';
});

const anim = document.getElementById('weather-animation');
const weather = document.body.getAttribute('data-weather');

if (weather) {
    const condition = weather.toLowerCase();
    let animation = '';

    if (condition.includes('rain')) {
        animation = 'rainy.gif';
    } else if (condition.includes('snow')) {
        animation = 'snowy.gif';
    } else if (condition.includes('cloud')) {
        animation = 'cloudy.gif';
    } else if (condition.includes('storm') || condition.includes('thunder')) {
        animation = 'stormy.gif';
    } else if (condition.includes('fog') || condition.includes('mist') || condition.includes('haze')) {
        animation = 'foggy.gif';
    } else if (condition.includes('clear') || condition.includes('sun')) {
        animation = 'sunny.gif';
    }

    if (animation) {
        anim.src = `/static/weather_animations/${animation}`;
    }
}

function getLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            position => {
                const lat = position.coords.latitude;
                const lon = position.coords.longitude;

                fetch("/weather_by_location", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({ lat, lon })
                }).then(res => {
                    if (res.redirected) {
                        window.location.href = res.url;
                    }
                }).catch(error => {
                    alert("Lỗi khi lấy dữ liệu thời tiết.");
                });
            },
            () => alert("Không thể truy cập vị trí.")
        );
    } else {
        alert("Trình duyệt không hỗ trợ định vị.");
    }
}

document.getElementById('donViSelect').addEventListener('change', function () {
    this.form.submit(); // Gửi form khi người dùng chọn đơn vị nhiệt độ khác
});
document.getElementById("loading-msg").style.display = "none";

document.addEventListener("DOMContentLoaded", function () {
    if (!window.location.search.includes("city=")) {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                function (position) {
                    fetch("/weather_by_location", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json"
                        },
                        body: JSON.stringify({
                            lat: position.coords.latitude,
                            lon: position.coords.longitude
                        })
                    })
                    .then(response => {
                        if (response.redirected) {
                            window.location.href = response.url;
                        }
                    })
                    .catch(error => {
                        console.error("Lỗi khi gửi tọa độ:", error);
                    });
                },
                function (error) {
                    console.warn("Không thể lấy vị trí:", error);
                }
            );
        } else {
            console.warn("Trình duyệt không hỗ trợ geolocation.");
        }
    }
});

// Phần gợi ý tìm kiếm thành phố
const cityInput = document.getElementById('cityInput');
const suggestionsBox = document.getElementById('suggestions');

cityInput.addEventListener('input', () => {
    const query = cityInput.value.trim();

    if (query.length < 2) {
        suggestionsBox.style.display = 'none';
        suggestionsBox.innerHTML = '';
        return;
    }

    fetch(`/suggest_city?query=${encodeURIComponent(query)}`)
        .then(res => res.json())
        .then(data => {
            console.log(JSON.stringify(data, null, 2));
            if (data.length === 0) {
                suggestionsBox.style.display = 'none';
                suggestionsBox.innerHTML = '';
                return;
            }

            suggestionsBox.innerHTML = '';
            data.forEach(city => {
                const div = document.createElement('div');
                div.textContent = city.description; 
                div.addEventListener('click', () => {
                    cityInput.value = city.description;
                    suggestionsBox.style.display = 'none';
                    cityInput.form.submit();
                });
                suggestionsBox.appendChild(div);
            });
            suggestionsBox.style.display = 'block';
        })
        .catch(() => {
            suggestionsBox.style.display = 'none';
            suggestionsBox.innerHTML = '';
        });
});

// Ẩn gợi ý khi click ra ngoài
document.addEventListener('click', (e) => {
    if (!suggestionsBox.contains(e.target) && e.target !== cityInput) {
        suggestionsBox.style.display = 'none';
    }
});

if (weather) {
    const condition = weather.toLowerCase();
    let animation = '';
    let textClass = '';

    if (condition.includes('rain')) {
        animation = 'rainy.gif';
        textClass = 'weather-text-rainy';
    } else if (condition.includes('snow')) {
        animation = 'snowy.gif';
        textClass = 'weather-text-snowy';
    } else if (condition.includes('cloud')) {
        animation = 'cloudy.gif';
        textClass = 'weather-text-cloudy';
    } else if (condition.includes('storm') || condition.includes('thunder')) {
        animation = 'stormy.gif';
        textClass = 'weather-text-stormy';
    } else if (condition.includes('fog') || condition.includes('mist') || condition.includes('haze')) {
        animation = 'foggy.gif';
        textClass = 'weather-text-foggy';
    } else if (condition.includes('clear') || condition.includes('sun')) {
        animation = 'sunny.gif';
        textClass = 'weather-text-sunny';
    }

    if (textClass) {
        document.body.classList.add(textClass);
    }
}
