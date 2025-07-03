// ============ 달력 (기존 코드) ============
let currentMonth = 5;

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
        dayElement.className = 'calendar-day date';
        dayElement.textContent = i;
        dayElement.style.justifyContent = 'center';
        dayElement.addEventListener('click', () => {
            document.querySelectorAll('.calendar-day.selected').forEach(el => {
                el.classList.remove('selected');
            });
            dayElement.classList.add('selected');
        });
        if (isCurrentMonth && i === today.getDate()) {
            dayElement.classList.add('selected');
        }
        calendar.appendChild(dayElement);
    }
}

// ============ 그래프 타이틀/내용 전환 기능 ============
const chartColumnMap = {
    '해수면의 높이': { title: "📊 해수면의 높이 변화 추이", field: "tide_level" },
    '기압': { title: "📊 기압 변화 추이", field: "air_press" },
    '풍속': { title: "📊 풍속 변화 추이", field: "wind_speed" },
    '유속': { title: "📊 유속 변화 추이", field: "current_speed" },
    '풍향': { title: "📊 풍향 변화 추이", field: "wind_dir" },
    '유향': { title: "📊 유향 변화 추이", field: "current_dir" }
};

document.addEventListener('DOMContentLoaded', function() {
    // 달력 기능
    generateCalendar(currentMonth);
    document.querySelectorAll('.month-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.month-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            currentMonth = parseInt(this.dataset.month);
            generateCalendar(currentMonth);
        });
    });
    document.getElementById('prevMonth').addEventListener('click', function() {
        if (currentMonth > 1) {
            currentMonth--;
            document.querySelectorAll('.month-btn').forEach(b => {
                b.classList.toggle('active', parseInt(b.dataset.month) === currentMonth);
            });
            generateCalendar(currentMonth);
        }
    });
    document.getElementById('nextMonth').addEventListener('click', function() {
        if (currentMonth < 12) {
            currentMonth++;
            document.querySelectorAll('.month-btn').forEach(b => {
                b.classList.toggle('active', parseInt(b.dataset.month) === currentMonth);
            });
            generateCalendar(currentMonth);
        }
    });

    // 컬럼 버튼 클릭 시 그래프 타이틀/내용 바꾸기
    document.querySelectorAll('.column-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            // 활성화 표시
            document.querySelectorAll('.column-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');

            // 그래프 타이틀/내용 변경
            const selected = this.textContent.trim();
            const titleEl = document.getElementById('chartTitle');
            // 그래프 제목 변경
            if (chartColumnMap[selected]) {
                titleEl.textContent = chartColumnMap[selected].title;
                // 만약 항목 따라 다른 그래프 이미지를 띄우고 싶으면 아래 코드 사용:
                // document.getElementById('chartImg').src = '/incheon/graph.png?start=' + encodeURIComponent(chartStart) + '&type=' + chartColumnMap[selected].field;
            }
        });
    });

    // ============ 그래프 이미지 슬라이딩 (6시간 단위) ============
    let chartStart = '2025-05-31 21:00:00'; // 기본 시작시간

    function updateChartImg() {
        document.getElementById('chartImg').src = '/incheon/graph.png?start=' + encodeURIComponent(chartStart);
    }

    // 좌우 버튼 이벤트
    document.getElementById('prevMonth').addEventListener('click', function(e) {
        e.preventDefault(); // 혹시 버튼이 form이면 새로고침 방지
        let dt = new Date(chartStart.replace(/-/g, '/'));
        dt.setHours(dt.getHours() - 6);
        chartStart =
            dt.getFullYear() + '-' +
            String(dt.getMonth() + 1).padStart(2, '0') + '-' +
            String(dt.getDate()).padStart(2, '0') + ' ' +
            String(dt.getHours()).padStart(2, '0') + ':00:00';
        updateChartImg();
    });
    document.getElementById('nextMonth').addEventListener('click', function(e) {
        e.preventDefault();
        let dt = new Date(chartStart.replace(/-/g, '/'));
        dt.setHours(dt.getHours() + 6);
        chartStart =
            dt.getFullYear() + '-' +
            String(dt.getMonth() + 1).padStart(2, '0') + '-' +
            String(dt.getDate()).padStart(2, '0') + ' ' +
            String(dt.getHours()).padStart(2, '0') + ':00:00';
        updateChartImg();
    });
});
