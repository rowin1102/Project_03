let currentMonth = 5;
const currentYear = 2025;

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

let chartStart = '2025-05-31 21:00:00';
let hour = 6;
let currentCol = 'sea_high';

function pad(n) { return String(n).padStart(2, '0'); }

function updateChartImg() {
    const dt = new Date(chartStart.replace(/-/g, '/'));
    const y = dt.getFullYear();
    const m = pad(dt.getMonth() + 1);
    const d = pad(dt.getDate());
    const h = pad(dt.getHours());
    const min = pad(dt.getMinutes());

    if (currentCol === 'wind_dir') {
        document.getElementById('chartImg').style.display = 'none';
        document.getElementById('chartPlaceholder').style.display = 'block';
        document.getElementById('timeRange').innerText =
            `${y}-${m}-${d} ${h}:${min} ~ ` +
            `${new Date(dt.getTime() + hour * 60 * 60 * 1000).toISOString().slice(11, 16)}`;
        if (typeof drawWindDirPlotly === 'function') drawWindDirPlotly(chartStart, hour);
        return;
    }
    if (currentCol === 'sea_dir_i') {
        document.getElementById('chartImg').style.display = 'none';
        document.getElementById('chartPlaceholder').style.display = 'block';
        document.getElementById('timeRange').innerText =
            `${y}-${m}-${d} ${h}:${min} ~ ` +
            `${new Date(dt.getTime() + hour * 60 * 60 * 1000).toISOString().slice(11, 16)}`;
        if (typeof drawSeaDirPlotly === 'function') drawSeaDirPlotly(chartStart, hour);
        return;
    }

    document.getElementById('chartPlaceholder').style.display = 'none';
    document.getElementById('chartImg').style.display = 'block';

    let src = `/taean/graph.png?start=${y}-${m}-${d} ${h}:${min}:00&col=${currentCol}&_=` + Date.now();
    const img = document.getElementById('chartImg');
    img.style.opacity = 0;
    img.onload = function () { img.style.opacity = 1; };
    img.src = src;

    document.getElementById('timeRange').innerText =
        `${y}-${m}-${d} ${h}:${min} ~ ` +
        `${new Date(dt.getTime() + hour * 60 * 60 * 1000).toISOString().slice(11, 16)}`;
}

function setChartStartFromDate(y, m, d) {
    chartStart = `${y}-${pad(m)}-${pad(d)} 00:00:00`;
}

document.addEventListener('DOMContentLoaded', function () {
    generateCalendar(currentMonth);

    document.querySelectorAll('.month-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            document.querySelectorAll('.month-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            currentMonth = parseInt(this.dataset.month);
            generateCalendar(currentMonth);
        });
    });

    document.getElementById('calendar').onclick = function (e) {
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

    document.querySelectorAll('.column-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            document.querySelectorAll('.column-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentCol = btn.dataset.col;
            document.getElementById('chartTitle').innerText = "📊 " + btn.innerText;
            updateChartImg();
        });
    });

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

    updateChartImg();
});
