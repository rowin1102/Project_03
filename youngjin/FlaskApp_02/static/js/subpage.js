// static/js/subpage.js

let currentMonth = 5;
const currentYear = 2025;
let chartStart   = '2025-05-31 21:00:00';
let hour         = 6;
let currentCol   = 'sea_high';
const pad        = n => String(n).padStart(2, '0');

function generateCalendar(month) {
  const calendar = document.getElementById('calendar');
  calendar.innerHTML = '';
  const weekdays = ['일','월','화','수','목','금','토'];
  weekdays.forEach(day => {
    const el = document.createElement('div');
    el.className = 'calendar-day header';
    el.textContent = day;
    calendar.appendChild(el);
  });
  const daysInMonth = month === 4 ? 30 : (month === 5 ? 31 : 30);
  const today = new Date();
  const isCurr = (month === today.getMonth()+1);
  for (let i=1; i<=daysInMonth; i++) {
    const el = document.createElement('div');
    el.className = 'calendar-day calendar-date date';
    el.textContent = i;
    el.style.justifyContent = 'center';
    const dateStr = `${currentYear}-${pad(month)}-${pad(i)}`;
    el.dataset.date = dateStr;
    if (isCurr && i===today.getDate()) el.classList.add('selected');
    calendar.appendChild(el);
  }
}

function setChartStartFromDate(y,m,d) {
  chartStart = `${y}-${pad(m)}-${pad(d)} 00:00:00`;
}

function updateChartImg() {
  const img      = document.getElementById('chartImg');
  const seaEl    = document.getElementById('seaDirChart');
  const windEl   = document.getElementById('windDirChart');
  const tsLegend = document.getElementById('tsLegend');
  const dirLegend= document.getElementById('dirLegend');
  const titleEl  = document.getElementById('chartTitle');
  const rangeEl  = document.getElementById('timeRange');

  // 모두 감추기
  img.style.display      = 'none';
  seaEl.style.display    = 'none';
  windEl.style.display   = 'none';
  tsLegend.style.display = 'none';
  dirLegend.style.display= 'none';

  const dt  = new Date(chartStart.replace(/-/g,'/'));
  const y   = dt.getFullYear(), m=pad(dt.getMonth()+1), d=pad(dt.getDate());
  const h   = pad(dt.getHours()), min=pad(dt.getMinutes());
  const end = new Date(dt.getTime() + hour*3600*1000);
  const rangeText = `${y}-${m}-${d} ${h}:${min} ~ ${pad(end.getHours())}:${pad(end.getMinutes())}`;
  rangeEl.innerText = rangeText;

  if (currentCol==='wind_dir') {
    // 풍향
    dirLegend.style.display = 'flex';
    windEl.style.display    = 'block';
    drawWindDirPlotly();
  }
  else if (currentCol==='sea_dir_i') {
    // 유향
    dirLegend.style.display = 'flex';
    seaEl.style.display     = 'block';
    drawSeaDirPlotly();
  }
  else {
    // 시계열: sea_high, pressure, wind_speed, sea_speed
    tsLegend.style.display = 'flex';
    titleEl.textContent = {
      sea_high:   '📊 해수면의 높이',
      pressure:   '📊 기압',
      wind_speed: '📊 풍속',
      sea_speed:  '📊 유속'
    }[currentCol] || '';
    const src = `/taean/graph.png?start=${y}-${m}-${d}+${h}:${min}:00&col=${currentCol}&_=${Date.now()}`;
    img.style.opacity = 0;
    img.onload = ()=> img.style.opacity = 1;
    img.src    = src;
    img.style.display = 'block';
  }
}

document.addEventListener('DOMContentLoaded', () => {
  generateCalendar(currentMonth);

  // month buttons
  document.querySelectorAll('.month-btn').forEach(btn=>{
    btn.addEventListener('click', function(){
      document.querySelectorAll('.month-btn').forEach(b=>b.classList.remove('active'));
      this.classList.add('active');
      currentMonth = +this.dataset.month;
      generateCalendar(currentMonth);
    });
  });

  // calendar date click
  document.getElementById('calendar').onclick = e => {
    const el = e.target;
    if (!el.classList.contains('calendar-date')) return;
    document.querySelectorAll('.calendar-date.selected')
            .forEach(s=>s.classList.remove('selected'));
    el.classList.add('selected');
    const [y,m,d] = el.dataset.date.split('-');
    setChartStartFromDate(y,m,d);
    updateChartImg();
  };

  // column buttons
  document.querySelectorAll('.column-btn').forEach(btn=>{
    btn.addEventListener('click', function(){
      document.querySelectorAll('.column-btn').forEach(b=>b.classList.remove('active'));
      this.classList.add('active');
      currentCol = this.dataset.col;
      updateChartImg();
    });
  });

  // prev/next buttons
  document.getElementById('prevBtn').onclick = () => {
    const dt = new Date(chartStart.replace(/-/g,'/'));
    dt.setHours(dt.getHours() - hour);
    chartStart = `${dt.getFullYear()}-${pad(dt.getMonth()+1)}-${pad(dt.getDate())} ${pad(dt.getHours())}:00:00`;
    updateChartImg();
  };
  document.getElementById('nextBtn').onclick = () => {
    const dt = new Date(chartStart.replace(/-/g,'/'));
    dt.setHours(dt.getHours() + hour);
    chartStart = `${dt.getFullYear()}-${pad(dt.getMonth()+1)}-${pad(dt.getDate())} ${pad(dt.getHours())}:00:00`;
    updateChartImg();
  };

  // 최초 렌더링
  updateChartImg();
});
