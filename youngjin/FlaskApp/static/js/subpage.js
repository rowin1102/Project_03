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

// ============ 초기 실행 ============
document.addEventListener('DOMContentLoaded', function () {
    // 달력 생성
    generateCalendar(currentMonth);

    // 월 선택 버튼 처리
    document.querySelectorAll('.month-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            document.querySelectorAll('.month-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');

            currentMonth = parseInt(this.dataset.month);
            generateCalendar(currentMonth);
        });
    });
});
