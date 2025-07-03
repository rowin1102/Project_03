// ============ 달력 (기존 코드) ============
let currentMonth = 5;
const currentYear = 2025; // 연도 고정

function generateCalendar(month) {
    const calendar = document.getElementById('calendar');
    calendar.innerHTML = '';
    const weekdays = ['일', '월', '화', '수', '목', '금', '토'];
    weekdays.forEach(day => {
        const dayElement = document.createElement('div');
        dayElement.className = 'calendar-day header';
        dayElement.textContent = day;
        calendar.appendChild(dayElement);
    });
    const daysInMonth = month === 4 ? 30 : (month === 5 ? 31 : 30);
    const today = new Date();
    const isCurrentMonth = (month === today.getMonth() + 1);
    for (let i = 1; i <= daysInMonth; i++) {
        const dayElement = document.createElement('div');
        dayElement.className = 'calendar-day calendar-date date';
        dayElement.textContent = i;
        dayElement.style.justifyContent = 'center';
        dayElement.setAttribute('data-date', `${currentYear}-${String(month).padStart(2, '0')}-${String(i).padStart(2, '0')}`);
        if (isCurrentMonth && i === today.getDate()) {
            dayElement.classList.add('selected');
        }
        calendar.appendChild(dayElement);
    }
}

// ============ 그래프/컬럼/구간 이동 통합 ============

let chartStart = '2025-05-31 21:00:00'; // 기본 시작시간
let hour = 6; // 6시간 단위
let currentCol = 'sea_high';

function pad(n) { return String(n).padStart(2, '0'); }

function updateChartImg() {
    const dt = new Date(chartStart.replace(/-/g, '/'));
    const y = dt.getFullYear();
    const m = pad(dt.getMonth() + 1);
    const d = pad(dt.getDate());
    const h = pad(dt.getHours());
    const min = pad(dt.getMinutes());
    let src;
    if (currentCol === 'wind_dir') {
        src = `/taean/wind_dir_graph.png?start=${y}-${m}-${d} ${h}:${min}:00&_=` + Date.now();
    } else if (currentCol === 'sea_dir_i') {
        src = `/taean/sea_dir_graph.png?start=${y}-${m}-${d} ${h}:${min}:00&_=` + Date.now();
    } else {
        src = `/taean/graph.png?start=${y}-${m}-${d} ${h}:${min}:00&col=${currentCol}&_=` + Date.now();
    }
    const img = document.getElementById('chartImg');
    img.style.opacity = 0;
    img.onload = function () { img.style.opacity = 1; };
    img.src = src;
    // 시간범위 표시
    document.getElementById('timeRange').innerText =
        `${y}-${m}-${d} ${h}:${min} ~ ` +
        `${new Date(dt.getTime() + hour * 60 * 60 * 1000).toISOString().slice(11, 16)}`;
}

function setChartStartFromDate(y, m, d) {
    chartStart = `${y}-${pad(m)}-${pad(d)} 00:00:00`;
}

// DOMContentLoaded 이후 바인딩
document.addEventListener('DOMContentLoaded', function() {
    // 달력 생성 및 월 버튼 바인딩
    generateCalendar(currentMonth);
    document.querySelectorAll('.month-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.month-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            currentMonth = parseInt(this.dataset.month);
            generateCalendar(currentMonth);
        });
    });

    // 달력 날짜(동적) 클릭 → 그래프 구간 변경 (이벤트 위임)
    document.getElementById('calendar').onclick = function(e) {
        let btn = e.target;
        if (btn.classList.contains('calendar-date') && btn.hasAttribute('data-date')) {
            const ymd = btn.getAttribute('data-date');
            if (!ymd) return;
            document.querySelectorAll('.calendar-date.selected').forEach(el => el.classList.remove('selected'));
            btn.classList.add('selected');
            const [y, m, d] = ymd.split('-');
            setChartStartFromDate(y, m, d);
            updateChartImg();
        }
    };

    // 컬럼 버튼 클릭(동적) → 그래프 컬럼 전환
    document.querySelectorAll('.column-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.column-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentCol = btn.dataset.col;
            document.getElementById('chartTitle').innerText = "📊 " + btn.innerText;
            updateChartImg();
        });
    });

    // 좌/우 구간 이동
    document.getElementById('prevBtn').onclick = function () {
        let dt = new Date(chartStart.replace(/-/g, '/'));
        dt.setHours(dt.getHours() - hour);
        chartStart =
            dt.getFullYear() + '-' +
            pad(dt.getMonth() + 1) + '-' +
            pad(dt.getDate()) + ' ' +
            pad(dt.getHours()) + ':00:00';
        updateChartImg();
    };
    document.getElementById('nextBtn').onclick = function () {
        let dt = new Date(chartStart.replace(/-/g, '/'));
        dt.setHours(dt.getHours() + hour);
        chartStart =
            dt.getFullYear() + '-' +
            pad(dt.getMonth() + 1) + '-' +
            pad(dt.getDate()) + ' ' +
            pad(dt.getHours()) + ':00:00';
        updateChartImg();
    };

    // 최초 표시
    updateChartImg();
});
