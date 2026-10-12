import json
import os

with open('powerbi_ready/dashboard_data.json', 'r', encoding='utf-8') as f:
    raw_data = f.read()

template = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Indian Cities Climate & Weather Analytics - Interactive Dashboard Preview</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<link href="https://fonts.googleapis.com/css2?family=Segoe+UI:wght@300;400;500;600;700&display=swap" rel="stylesheet" />
<style>
  :root {
    --bg-page: #f8fafc;
    --bg-card: #ffffff;
    --border-color: #e2e8f0;
    --text-primary: #0f172a;
    --text-secondary: #64748b;
    --primary-blue: #1e88e5;
    --accent-orange: #fb8c00;
    --accent-red: #d81b60;
    --accent-teal: #00897b;
    --accent-purple: #5e35b1;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif; }
  body { background: var(--bg-page); color: var(--text-primary); min-height: 100vh; display: flex; flex-direction: column; }
  header { background: #ffffff; border-bottom: 1px solid var(--border-color); padding: 14px 24px; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
  .title-group h1 { font-size: 1.25rem; font-weight: 700; color: var(--text-primary); }
  .title-group p { font-size: 0.82rem; color: var(--text-secondary); margin-top: 2px; }
  .tag-badge { background: #e0f2fe; color: #0369a1; font-size: 0.72rem; font-weight: 600; padding: 4px 10px; border-radius: 999px; text-transform: uppercase; letter-spacing: 0.5px; }

  /* Navigation Bar */
  .nav-tabs { background: #ffffff; border-bottom: 1px solid var(--border-color); display: flex; padding: 0 24px; gap: 8px; }
  .tab-btn { background: none; border: none; padding: 12px 18px; font-size: 0.9rem; font-weight: 600; color: var(--text-secondary); cursor: pointer; border-bottom: 3px solid transparent; transition: all 0.2s; }
  .tab-btn:hover { color: var(--primary-blue); }
  .tab-btn.active { color: var(--primary-blue); border-bottom-color: var(--primary-blue); }

  .content-area { padding: 20px 24px; flex: 1; max-width: 1600px; width: 100%; margin: 0 auto; }
  .page-view { display: none; }
  .page-view.active { display: block; }

  /* Slicers Row */
  .slicers-bar { background: #ffffff; border: 1px solid var(--border-color); border-radius: 8px; padding: 12px 18px; margin-bottom: 18px; display: flex; gap: 16px; flex-wrap: wrap; align-items: center; box-shadow: 0 1px 2px rgba(0,0,0,0.03); }
  .slicer-item { display: flex; align-items: center; gap: 8px; font-size: 0.85rem; font-weight: 600; color: var(--text-secondary); }
  .slicer-item select { padding: 6px 12px; font-size: 0.85rem; border: 1px solid var(--border-color); border-radius: 6px; background: #fff; color: var(--text-primary); outline: none; cursor: pointer; }

  /* KPI Grid */
  .kpi-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); gap: 14px; margin-bottom: 20px; }
  .kpi-card { background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 8px; padding: 14px 18px; box-shadow: 0 2px 4px rgba(0,0,0,0.03); position: relative; overflow: hidden; }
  .kpi-card::before { content: ""; position: absolute; left: 0; top: 0; bottom: 0; width: 4px; background: var(--primary-blue); }
  .kpi-card.orange::before { background: var(--accent-orange); }
  .kpi-card.red::before { background: var(--accent-red); }
  .kpi-card.teal::before { background: var(--accent-teal); }
  .kpi-card.purple::before { background: var(--accent-purple); }
  .kpi-label { font-size: 0.76rem; font-weight: 600; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.5px; }
  .kpi-value { font-size: 1.55rem; font-weight: 700; color: var(--text-primary); margin-top: 4px; }
  .kpi-sub { font-size: 0.72rem; color: var(--text-secondary); margin-top: 2px; }

  /* Grid Layouts */
  .grid-split { display: grid; grid-template-columns: 1.15fr 0.85fr; gap: 18px; margin-bottom: 20px; }
  .grid-2x2 { display: grid; grid-template-columns: 1fr 1fr; gap: 18px; margin-bottom: 20px; }
  .card-container { background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 8px; padding: 16px; box-shadow: 0 2px 5px rgba(0,0,0,0.03); }
  .card-header { font-size: 0.92rem; font-weight: 600; color: var(--text-primary); margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center; }

  /* Map Container */
  #map { height: 480px; width: 100%; border-radius: 6px; }

  /* Heatmap Table */
  .heatmap-table { width: 100%; border-collapse: collapse; font-size: 0.75rem; text-align: center; }
  .heatmap-table th { background: #f1f5f9; padding: 6px; border: 1px solid var(--border-color); font-weight: 600; }
  .heatmap-table td { padding: 6px 4px; border: 1px solid #f1f5f9; font-weight: 500; }
  .heatmap-table td.city-col { text-align: left; font-weight: 600; background: #fff; border-right: 2px solid var(--border-color); padding-left: 8px; }

  @media (max-width: 1024px) {
    .grid-split, .grid-2x2 { grid-template-columns: 1fr; }
  }
</style>
</head>
<body>

<header>
  <div class="title-group">
    <h1>Indian Cities Climate & Weather Analytics</h1>
    <p>Apache Spark Big Data Analytics Pipeline & Power BI Interactive Dashboard</p>
  </div>
  <div>
    <span class="tag-badge">Apache Spark 4.0 &middot; 2.3M+ Observations &middot; 50 Cities</span>
  </div>
</header>

<nav class="nav-tabs">
  <button class="tab-btn active" onclick="showPage(1)">Page 1: India Climate Overview</button>
  <button class="tab-btn" onclick="showPage(2)">Page 2: City Comparison</button>
  <button class="tab-btn" onclick="showPage(3)">Page 3: Seasonality & Trends</button>
</nav>

<div class="content-area">

  <!-- ==================== PAGE 1 ==================== -->
  <div id="page1" class="page-view active">
    <div class="slicers-bar">
      <div class="slicer-item">
        <span>Year:</span>
        <select id="p1-year" onchange="updatePage1()">
          <option value="all">All Years (2020-2025)</option>
          <option value="2020">2020</option>
          <option value="2021">2021</option>
          <option value="2022">2022</option>
          <option value="2023">2023</option>
          <option value="2024">2024</option>
          <option value="2025">2025</option>
        </select>
      </div>
      <div class="slicer-item">
        <span>Season:</span>
        <select id="p1-season" onchange="updatePage1()">
          <option value="all">All Seasons</option>
          <option value="Winter">Winter (Dec-Feb)</option>
          <option value="Summer">Summer (Mar-May)</option>
          <option value="Monsoon">Monsoon (Jun-Sep)</option>
          <option value="Post-Monsoon">Post-Monsoon (Oct-Nov)</option>
        </select>
      </div>
      <div class="slicer-item">
        <span>City Filter:</span>
        <select id="p1-city" onchange="updatePage1()">
          <option value="all">All 50 Cities</option>
        </select>
      </div>
    </div>

    <div class="kpi-row">
      <div class="kpi-card">
        <div class="kpi-label">Average Temperature</div>
        <div class="kpi-value" id="kpi-avg-temp">-- °C</div>
        <div class="kpi-sub">Mean across selected scope</div>
      </div>
      <div class="kpi-card orange">
        <div class="kpi-label">Maximum Temperature</div>
        <div class="kpi-value" id="kpi-max-temp">-- °C</div>
        <div class="kpi-sub" id="kpi-hottest-sub">Hottest recorded peak</div>
      </div>
      <div class="kpi-card teal">
        <div class="kpi-label">Total Rainfall</div>
        <div class="kpi-value" id="kpi-total-rain">-- mm</div>
        <div class="kpi-sub" id="kpi-wettest-sub">Total precipitation</div>
      </div>
      <div class="kpi-card purple">
        <div class="kpi-label">Average Humidity</div>
        <div class="kpi-value" id="kpi-avg-humidity">-- %</div>
        <div class="kpi-sub">Relative moisture level</div>
      </div>
      <div class="kpi-card red">
        <div class="kpi-label">Hottest City</div>
        <div class="kpi-value" style="font-size: 1.25rem;" id="kpi-hottest-city">--</div>
        <div class="kpi-sub" id="kpi-hottest-val">Peak temperature</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Wettest City</div>
        <div class="kpi-value" style="font-size: 1.25rem;" id="kpi-wettest-city">--</div>
        <div class="kpi-sub" id="kpi-wettest-val">Highest accumulated rain</div>
      </div>
    </div>

    <div class="grid-split">
      <div class="card-container">
        <div class="card-header">
          <span>Interactive India Weather Map (Coordinates &middot; Bubble Size: Rainfall &middot; Color: Temp)</span>
        </div>
        <div id="map"></div>
      </div>
      <div style="display:flex; flex-direction:column; gap:18px;">
        <div class="card-container" style="flex:1;">
          <div class="card-header">Top 10 Hottest Cities (Max Recorded Temp °C)</div>
          <div style="height:210px;"><canvas id="chart-top-hottest"></canvas></div>
        </div>
        <div class="card-container" style="flex:1;">
          <div class="card-header">Top 10 Rainiest Cities (Total Precipitation mm)</div>
          <div style="height:210px;"><canvas id="chart-top-rainiest"></canvas></div>
        </div>
      </div>
    </div>
  </div>

  <!-- ==================== PAGE 2 ==================== -->
  <div id="page2" class="page-view">
    <div class="slicers-bar">
      <div class="slicer-item">
        <span>Select Cities to Compare:</span>
        <select id="p2-city1" onchange="updatePage2()"></select>
        <select id="p2-city2" onchange="updatePage2()"></select>
        <select id="p2-city3" onchange="updatePage2()"></select>
      </div>
    </div>

    <div class="grid-2x2">
      <div class="card-container">
        <div class="card-header">Monthly Temperature Profile (°C)</div>
        <div style="height: 280px;"><canvas id="chart-p2-temp-line"></canvas></div>
      </div>
      <div class="card-container">
        <div class="card-header">Highs vs Lows Range by City (°C)</div>
        <div style="height: 280px;"><canvas id="chart-p2-extremes-bar"></canvas></div>
      </div>
      <div class="card-container">
        <div class="card-header">Precipitation (mm) vs Humidity (%) Dynamics</div>
        <div style="height: 280px;"><canvas id="chart-p2-rain-hum-combo"></canvas></div>
      </div>
      <div class="card-container">
        <div class="card-header">Atmospheric Comfort: Wind Speed vs Humidity Dispersion</div>
        <div style="height: 280px;"><canvas id="chart-p2-scatter"></canvas></div>
      </div>
    </div>
  </div>

  <!-- ==================== PAGE 3 ==================== -->
  <div id="page3" class="page-view">
    <div class="card-container" style="margin-bottom: 20px;">
      <div class="card-header">Monsoon Rainfall Timeline across Calendar Months (Surge June - September)</div>
      <div style="height: 260px;"><canvas id="chart-p3-rain-timeline"></canvas></div>
    </div>

    <div class="grid-split" style="margin-bottom: 20px;">
      <div class="card-container" style="max-height: 440px; overflow-y: auto;">
        <div class="card-header">City &times; Month Temperature Heatmap (°C)</div>
        <table class="heatmap-table" id="heatmap-table">
          <!-- Populated by JS -->
        </table>
      </div>
      <div style="display:flex; flex-direction:column; gap:18px;">
        <div class="card-container" style="flex:1;">
          <div class="card-header">Seasonal Rainfall Contribution (%)</div>
          <div style="height: 180px;"><canvas id="chart-p3-season-donut"></canvas></div>
        </div>
        <div class="card-container" style="flex:1;">
          <div class="card-header">Multi-Year Longitudinal Climate Trends (2020-2025)</div>
          <div style="height: 180px;"><canvas id="chart-p3-yoy-line"></canvas></div>
        </div>
      </div>
    </div>
  </div>

</div>

<script>
const rawData = """ + raw_data + """;
const cities = rawData.cities;
const monthly = rawData.monthly;

let mapInstance = null;
let mapMarkers = [];
let charts = {};

function initApp() {
  populateCityDropdowns();
  initMap();
  updatePage1();
  initPage2();
  initPage3();
}

function showPage(pageNo) {
  document.querySelectorAll('.tab-btn').forEach((b, i) => b.classList.toggle('active', i === pageNo - 1));
  document.querySelectorAll('.page-view').forEach((p, i) => p.classList.toggle('active', i === pageNo - 1));
  if (pageNo === 1 && mapInstance) {
    setTimeout(() => mapInstance.invalidateSize(), 200);
  }
}

function populateCityDropdowns() {
  const p1City = document.getElementById('p1-city');
  const p2c1 = document.getElementById('p2-city1');
  const p2c2 = document.getElementById('p2-city2');
  const p2c3 = document.getElementById('p2-city3');

  cities.forEach(c => {
    const opt = document.createElement('option');
    opt.value = c.city_name;
    opt.textContent = c.city_name;
    p1City.appendChild(opt.cloneNode(true));
    p2c1.appendChild(opt.cloneNode(true));
    p2c2.appendChild(opt.cloneNode(true));
    p2c3.appendChild(opt.cloneNode(true));
  });

  p2c1.value = 'Delhi';
  p2c2.value = 'Mumbai';
  p2c3.value = 'Bangalore';
}

function getSeason(m) {
  if ([12, 1, 2].includes(m)) return 'Winter';
  if ([3, 4, 5].includes(m)) return 'Summer';
  if ([6, 7, 8, 9].includes(m)) return 'Monsoon';
  return 'Post-Monsoon';
}

function initMap() {
  mapInstance = L.map('map').setView([21.8, 78.9], 4.5);
  L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; OpenStreetMap contributors &copy; CARTO',
    subdomains: 'abcd',
    maxZoom: 18
  }).addTo(mapInstance);
}

function updatePage1() {
  const selectedYear = document.getElementById('p1-year').value;
  const selectedSeason = document.getElementById('p1-season').value;
  const selectedCity = document.getElementById('p1-city').value;

  let filtered = monthly.filter(r => {
    if (selectedYear !== 'all' && r.y !== parseInt(selectedYear)) return false;
    if (selectedSeason !== 'all' && getSeason(r.m) !== selectedSeason) return false;
    if (selectedCity !== 'all' && r.c !== selectedCity) return false;
    return true;
  });

  let totalRain = filtered.reduce((s, r) => s + r.p, 0);
  let avgTemp = filtered.length ? (filtered.reduce((s, r) => s + r.t, 0) / filtered.length).toFixed(1) : 0;
  let avgHum = filtered.length ? (filtered.reduce((s, r) => s + r.h, 0) / filtered.length).toFixed(1) : 0;

  document.getElementById('kpi-avg-temp').textContent = avgTemp + ' °C';
  document.getElementById('kpi-total-rain').textContent = Math.round(totalRain).toLocaleString() + ' mm';
  document.getElementById('kpi-avg-humidity').textContent = avgHum + ' %';

  let cityScope = selectedCity !== 'all' ? cities.filter(c => c.city_name === selectedCity) : cities;
  let hottest = cityScope.slice().sort((a,b) => b.max_temp - a.max_temp)[0];
  let wettest = cityScope.slice().sort((a,b) => b.total_rain - a.total_rain)[0];

  if (hottest) {
    document.getElementById('kpi-max-temp').textContent = hottest.max_temp + ' °C';
    document.getElementById('kpi-hottest-city').textContent = hottest.city_name;
    document.getElementById('kpi-hottest-val').textContent = hottest.max_temp + ' °C max record';
  }
  if (wettest) {
    document.getElementById('kpi-wettest-city').textContent = wettest.city_name;
    document.getElementById('kpi-wettest-val').textContent = Math.round(wettest.total_rain).toLocaleString() + ' mm total';
  }

  mapMarkers.forEach(m => mapInstance.removeLayer(m));
  mapMarkers = [];

  cityScope.forEach(c => {
    const tempRatio = Math.min(1, Math.max(0, (c.avg_temp - 20) / 15));
    const r = Math.round(30 + tempRatio * 186);
    const g = Math.round(136 - tempRatio * 109);
    const b = Math.round(229 - tempRatio * 133);
    const color = `rgb(${r},${g},${b})`;
    const radius = Math.max(7, Math.min(22, (c.total_rain / 500)));

    const marker = L.circleMarker([c.lat, c.lng], {
      radius: radius,
      fillColor: color,
      color: '#ffffff',
      weight: 1.5,
      opacity: 0.9,
      fillOpacity: 0.8
    }).addTo(mapInstance);

    marker.bindPopup(`
      <div style="font-size:12px; line-height:1.5;">
        <strong style="font-size:14px;">${c.city_name}</strong><br/>
        <b>Avg Temperature:</b> ${c.avg_temp} °C<br/>
        <b>Max Temp:</b> ${c.max_temp} °C &middot; <b>Min:</b> ${c.min_temp} °C<br/>
        <b>Total Rainfall:</b> ${Math.round(c.total_rain).toLocaleString()} mm<br/>
        <b>Avg Humidity:</b> ${c.avg_humidity} %<br/>
        <b>Population:</b> ${c.population.toLocaleString()}
      </div>
    `);
    mapMarkers.push(marker);
  });

  const topHottest = cities.slice().sort((a,b) => b.max_temp - a.max_temp).slice(0, 10);
  const topRainiest = cities.slice().sort((a,b) => b.total_rain - a.total_rain).slice(0, 10);

  renderHorizontalBar('chart-top-hottest', topHottest.map(c => c.city_name), topHottest.map(c => c.max_temp), '#fb8c00', 'Max Temp (°C)');
  renderHorizontalBar('chart-top-rainiest', topRainiest.map(c => c.city_name), topRainiest.map(c => c.total_rain), '#1e88e5', 'Total Rain (mm)');
}

function renderHorizontalBar(id, labels, data, color, datasetLabel) {
  if (charts[id]) charts[id].destroy();
  const ctx = document.getElementById(id).getContext('2d');
  charts[id] = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: datasetLabel,
        data: data,
        backgroundColor: color,
        borderRadius: 4
      }]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: { color: '#f1f5f9' }, ticks: { font: { size: 10 } } },
        y: { ticks: { font: { size: 11, weight: 'bold' } } }
      }
    }
  });
}

function initPage2() {
  updatePage2();
}

function updatePage2() {
  const c1 = document.getElementById('p2-city1').value;
  const c2 = document.getElementById('p2-city2').value;
  const c3 = document.getElementById('p2-city3').value;
  const selected = [c1, c2, c3].filter((v, i, a) => a.indexOf(v) === i);

  const monthNames = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  const colors = ['#1e88e5', '#d81b60', '#00897b'];

  const datasetsLine = selected.map((cityName, idx) => {
    const monthlyVals = [];
    for (let m = 1; m <= 12; m++) {
      const records = monthly.filter(r => r.c === cityName && r.m === m);
      const avg = records.length ? (records.reduce((s, r) => s + r.t, 0) / records.length).toFixed(1) : 0;
      monthlyVals.push(parseFloat(avg));
    }
    return {
      label: cityName,
      data: monthlyVals,
      borderColor: colors[idx % colors.length],
      backgroundColor: colors[idx % colors.length] + '22',
      tension: 0.35,
      borderWidth: 2.5
    };
  });

  if (charts['p2-temp-line']) charts['p2-temp-line'].destroy();
  charts['p2-temp-line'] = new Chart(document.getElementById('chart-p2-temp-line').getContext('2d'), {
    type: 'line',
    data: { labels: monthNames, datasets: datasetsLine },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: { y: { title: { display: true, text: 'Temperature (°C)' } } }
    }
  });

  const selectedSummaries = selected.map(name => cities.find(c => c.city_name === name));
  if (charts['p2-extremes-bar']) charts['p2-extremes-bar'].destroy();
  charts['p2-extremes-bar'] = new Chart(document.getElementById('chart-p2-extremes-bar').getContext('2d'), {
    type: 'bar',
    data: {
      labels: selected,
      datasets: [
        { label: 'Max Temp (°C)', data: selectedSummaries.map(s => s ? s.max_temp : 0), backgroundColor: '#d81b60', borderRadius: 4 },
        { label: 'Min Temp (°C)', data: selectedSummaries.map(s => s ? s.min_temp : 0), backgroundColor: '#1e88e5', borderRadius: 4 }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: { y: { title: { display: true, text: 'Degrees (°C)' } } }
    }
  });

  const primaryCity = selected[0];
  const rainVals = [];
  const humVals = [];
  for (let m = 1; m <= 12; m++) {
    const recs = monthly.filter(r => r.c === primaryCity && r.m === m);
    rainVals.push(recs.length ? Math.round(recs.reduce((s, r) => s + r.p, 0) / (recs.length / 5)) : 0);
    humVals.push(recs.length ? parseFloat((recs.reduce((s, r) => s + r.h, 0) / recs.length).toFixed(1)) : 0);
  }

  if (charts['p2-rain-hum-combo']) charts['p2-rain-hum-combo'].destroy();
  charts['p2-rain-hum-combo'] = new Chart(document.getElementById('chart-p2-rain-hum-combo').getContext('2d'), {
    data: {
      labels: monthNames,
      datasets: [
        { type: 'bar', label: `Rainfall (mm) - ${primaryCity}`, data: rainVals, backgroundColor: '#1e88e588', yAxisID: 'yRain', borderRadius: 4 },
        { type: 'line', label: `Humidity (%) - ${primaryCity}`, data: humVals, borderColor: '#00897b', borderWidth: 2.5, yAxisID: 'yHum', tension: 0.3 }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        yRain: { type: 'linear', position: 'left', title: { display: true, text: 'Rainfall (mm)' } },
        yHum: { type: 'linear', position: 'right', min: 0, max: 100, title: { display: true, text: 'Humidity (%)' }, grid: { drawOnChartArea: false } }
      }
    }
  });

  const scatterData = cities.map(c => ({
    x: c.avg_wind,
    y: c.avg_humidity,
    city: c.city_name
  }));

  if (charts['p2-scatter']) charts['p2-scatter'].destroy();
  charts['p2-scatter'] = new Chart(document.getElementById('chart-p2-scatter').getContext('2d'), {
    type: 'scatter',
    data: {
      datasets: [{
        label: 'Indian Cities',
        data: scatterData,
        backgroundColor: '#5e35b1aa',
        borderColor: '#5e35b1',
        pointRadius: 6,
        pointHoverRadius: 9
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        tooltip: {
          callbacks: {
            label: (ctx) => `${ctx.raw.city}: Wind ${ctx.raw.x} km/h, Humidity ${ctx.raw.y}%`
          }
        }
      },
      scales: {
        x: { title: { display: true, text: 'Average Wind Speed (km/h)' } },
        y: { title: { display: true, text: 'Average Humidity (%)' } }
      }
    }
  });
}

function initPage3() {
  const monthNames = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];

  const monthlyRainAgg = [];
  for (let m = 1; m <= 12; m++) {
    const recs = monthly.filter(r => r.m === m);
    const sum = recs.reduce((s, r) => s + r.p, 0);
    monthlyRainAgg.push(Math.round(sum));
  }

  if (charts['p3-rain-timeline']) charts['p3-rain-timeline'].destroy();
  charts['p3-rain-timeline'] = new Chart(document.getElementById('chart-p3-rain-timeline').getContext('2d'), {
    type: 'line',
    data: {
      labels: monthNames,
      datasets: [{
        label: 'Aggregated National Rainfall (mm)',
        data: monthlyRainAgg,
        fill: true,
        backgroundColor: 'rgba(0, 137, 123, 0.25)',
        borderColor: '#00897b',
        borderWidth: 2.5,
        tension: 0.35
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: { y: { title: { display: true, text: 'Rainfall (mm)' } } }
    }
  });

  const table = document.getElementById('heatmap-table');
  table.innerHTML = '';
  let thead = '<thead><tr><th style="text-align:left; padding-left:8px;">City</th>';
  monthNames.forEach(m => thead += `<th>${m}</th>`);
  thead += '</tr></thead><tbody>';

  let tbody = '';
  cities.slice(0, 25).forEach(c => {
    tbody += `<tr><td class="city-col">${c.city_name}</td>`;
    for (let m = 1; m <= 12; m++) {
      const recs = monthly.filter(r => r.c === c.city_name && r.m === m);
      const val = recs.length ? (recs.reduce((s, r) => s + r.t, 0) / recs.length).toFixed(1) : 0;
      const ratio = Math.max(0, Math.min(1, (val - 15) / 22));
      const r = Math.round(224 + ratio * (239 - 224));
      const g = Math.round(242 - ratio * (242 - 68));
      const b = Math.round(254 - ratio * (254 - 68));
      const textColor = ratio > 0.65 ? '#ffffff' : '#0f172a';
      tbody += `<td style="background: rgb(${r},${g},${b}); color: ${textColor};">${val}</td>`;
    }
    tbody += '</tr>';
  });
  tbody += '</tbody>';
  table.innerHTML = thead + tbody;

  const seasonTotals = { 'Monsoon': 0, 'Summer': 0, 'Winter': 0, 'Post-Monsoon': 0 };
  monthly.forEach(r => {
    seasonTotals[getSeason(r.m)] += r.p;
  });

  if (charts['p3-season-donut']) charts['p3-season-donut'].destroy();
  charts['p3-season-donut'] = new Chart(document.getElementById('chart-p3-season-donut').getContext('2d'), {
    type: 'doughnut',
    data: {
      labels: Object.keys(seasonTotals),
      datasets: [{
        data: Object.values(seasonTotals).map(v => Math.round(v)),
        backgroundColor: ['#00897b', '#fb8c00', '#1e88e5', '#5e35b1'],
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { position: 'right' } }
    }
  });

  const years = [2020, 2021, 2022, 2023, 2024, 2025];
  const yearTemps = years.map(y => {
    const recs = monthly.filter(r => r.y === y);
    return recs.length ? parseFloat((recs.reduce((s, r) => s + r.t, 0) / recs.length).toFixed(2)) : null;
  });

  if (charts['p3-yoy-line']) charts['p3-yoy-line'].destroy();
  charts['p3-yoy-line'] = new Chart(document.getElementById('chart-p3-yoy-line').getContext('2d'), {
    type: 'line',
    data: {
      labels: years,
      datasets: [{
        label: 'National Avg Temp (°C)',
        data: yearTemps,
        borderColor: '#d81b60',
        backgroundColor: 'rgba(216, 27, 96, 0.1)',
        tension: 0.3,
        borderWidth: 2.5,
        fill: true
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: { y: { title: { display: true, text: 'Avg Temp (°C)' } } }
    }
  });
}

window.onload = initApp;
</script>

</body>
</html>"""

with open('powerbi_ready/dashboard_preview.html', 'w', encoding='utf-8') as f:
    f.write(template)

print("Generated powerbi_ready/dashboard_preview.html successfully.")
