import { useEffect, useState } from "react";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from "recharts";

import "./App.css";


/* ==================================================
   AI TEXT FORMATTER
================================================== */

function formatAIText(text) {

  if (!text) return null;

  return text.split("\n").map((line, index) => {

    const parts = line.split(/(\*\*.*?\*\*)/g);

    return (
      <div key={index} className="ai-line">

        {parts.map((part, partIndex) => {

          if (
            part.startsWith("**") &&
            part.endsWith("**")
          ) {

            return (
              <strong key={partIndex}>
                {part.slice(2, -2)}
              </strong>
            );

          }

          return (
            <span key={partIndex}>
              {part}
            </span>
          );

        })}

      </div>
    );

  });

}


/* ==================================================
   MAIN APP
================================================== */

function App() {

  const [crop, setCrop] = useState("Rice");

  const [sensorData, setSensorData] = useState([]);
  const [analysis, setAnalysis] = useState(null);
  const [weather, setWeather] = useState(null);

  const [aiAdvice, setAiAdvice] = useState(null);
  const [question, setQuestion] = useState("");
  const [aiLoading, setAiLoading] = useState(false);

  const [loading, setLoading] = useState(true);


  /* ==================================================
     FETCH SENSOR DATA
  ================================================== */

  const fetchSensorData = async () => {

    try {

      const response = await fetch(
        "http://127.0.0.1:8000/sensor-data"
      );

      const data = await response.json();

      setSensorData(data);

    } catch (error) {

      console.error(
        "Sensor data error:",
        error
      );

    }

  };


  /* ==================================================
     FETCH AGRICULTURE ANALYSIS
  ================================================== */

  const fetchAnalysis = async (selectedCrop) => {

    try {

      const response = await fetch(
        `http://127.0.0.1:8000/analysis?crop=${encodeURIComponent(selectedCrop)}`
      );

      const data = await response.json();

      if (data.status === "success") {

        setAnalysis(data.analysis);

      }

    } catch (error) {

      console.error(
        "Analysis error:",
        error
      );

    }

  };


  /* ==================================================
     FETCH WEATHER
  ================================================== */

  const fetchWeather = async () => {

    try {

      const response = await fetch(
        "http://127.0.0.1:8000/weather"
      );

      const data = await response.json();

      setWeather(data);

    } catch (error) {

      console.error(
        "Weather error:",
        error
      );

    }

  };


  /* ==================================================
     AI AGRICULTURAL ASSISTANT
  ================================================== */

  const fetchAIAdvice = async (
    selectedCrop,
    farmerQuestion
  ) => {

    if (!farmerQuestion.trim()) return;

    setAiLoading(true);

    try {

      const response = await fetch(
        `http://127.0.0.1:8000/ai-advice?crop=${encodeURIComponent(selectedCrop)}&question=${encodeURIComponent(farmerQuestion)}`
      );

      const data = await response.json();

      if (data.status === "success") {

        setAiAdvice(data.ai_advice);

      } else {

        setAiAdvice(
          "Unable to get AI advice right now."
        );

      }

    } catch (error) {

      console.error(
        "AI advice error:",
        error
      );

      setAiAdvice(
        "Unable to connect to the AI service."
      );

    } finally {

      setAiLoading(false);

    }

  };


  /* ==================================================
     LOAD DATA + AUTO REFRESH
  ================================================== */

  useEffect(() => {

    const loadData = async () => {

      await fetchSensorData();

      await fetchAnalysis(crop);

      await fetchWeather();

      setLoading(false);

    };


    loadData();


    const interval = setInterval(() => {

      fetchSensorData();

      fetchAnalysis(crop);

      fetchWeather();

    }, 5000);


    return () => clearInterval(interval);

  }, [crop]);


  /* ==================================================
     LATEST SENSOR READING
  ================================================== */

  const latestReading =
    sensorData.length > 0
      ? sensorData[sensorData.length - 1]
      : null;


  /* ==================================================
     CHART DATA
  ================================================== */

  const chartData = sensorData
    .slice(-20)
    .map((reading, index) => ({

      name: index + 1,

      temperature:
        reading.temperature,

      humidity:
        reading.humidity,

      soil:
        reading.soil_moisture

    }));


  /* ==================================================
     ALERT COUNT
  ================================================== */

  const issueCount =
    analysis?.issues?.length || 0;

  const warningCount =
    analysis?.warnings?.length || 0;

  const totalAlerts =
    issueCount + warningCount;


  /* ==================================================
     LOADING SCREEN
  ================================================== */

  if (loading) {

    return (

      <div className="loading-screen">

        <div className="loading-logo">
          <img
            src="/qubitscrew.png"
            alt="QubitsCrew"
          />
        </div>

        <h2>
          Multimodal AI-Powered
          Farm Advisory System
        </h2>

        <p>
          Initializing farm intelligence...
        </p>

      </div>

    );

  }


  /* ==================================================
     DASHBOARD
  ================================================== */

  return (

    <div className="app">


      {/* ==================================================
          TOP NAVIGATION
      ================================================== */}

      <nav className="top-nav">

        <div className="nav-brand">

          <div className="nav-leaf">
            🌱
          </div>

          <span>
            Smart Agriculture
          </span>

        </div>


        <div className="nav-links">

          <span className="nav-active">
            ▦ Dashboard
          </span>

          <span>
            ◫ Analytics
          </span>

          <span>
            ✦ AI Assistant
          </span>

          <span>
            ◈ Crop Guide
          </span>

          <span>
            ⚙ Settings
          </span>

        </div>


        <div className="nav-status">

          <span className="online-dot"></span>

          System Online

        </div>

      </nav>


      {/* ==================================================
          PROJECT HERO
      ================================================== */}

      <section className="project-hero">

        <div className="hero-logo">

          <img
            src="/qubitscrew.png"
            alt="QubitsCrew"
          />

          <div className="hero-tagline">
            INNOVATE • BUILD • IMPACT
          </div>

        </div>


        <div className="hero-divider"></div>


        <div className="hero-content">

          <span className="hero-kicker">
            AI + IoT AGRICULTURAL INTELLIGENCE
          </span>

          <h1>
            Multimodal{" "}
            <span>AI-Powered</span>
            <br />
            Farm Advisory System
          </h1>

          <p>
            Blending real-time IoT sensing,
            weather intelligence and multimodal AI
            to deliver personalized crop insights,
            irrigation guidance and proactive alerts
            for smarter, healthier farms.
          </p>


          <div className="hero-pills">

            <span>
              ◉ IoT Sensing
            </span>

            <span>
              ☁ Weather Intelligence
            </span>

            <span>
              ◉ AI Insights
            </span>

            <span>
              ▥ Better Harvests
            </span>

          </div>

        </div>


        <div className="hero-decoration">

          <div>
            Smarter
          </div>

          <div>
            Farms
          </div>

          <div>
            Brighter
          </div>

          <div>
            Tomorrows
          </div>

        </div>

      </section>


      {/* ==================================================
          SMART AGRICULTURE HEADER
      ================================================== */}

      <section className="system-card">

        <div className="system-icon">
          🌱
        </div>


        <div>

          <h2>
            Smart Agriculture
          </h2>

          <p>
            AI + IoT Based Smart Farming System
          </p>

        </div>


        <div className="system-right">

          <div className="system-online">

            <span className="online-dot"></span>

            System Online

          </div>

        </div>

      </section>


      {/* ==================================================
          FARM CONFIGURATION
      ================================================== */}

      <section className="control-card">

        <div className="control-icon">
          🌱
        </div>


        <div className="control-text">

          <span className="section-label">
            FARM CONFIGURATION
          </span>

          <h2>
            Select Crop
          </h2>

          <p>
            Choose the crop currently being monitored.
          </p>

        </div>


        <select
          value={crop}
          onChange={(event) => {

            setCrop(event.target.value);

            setAiAdvice(null);

          }}
        >

          <option value="Rice">
            🌾 Rice
          </option>

          <option value="Wheat">
            🌾 Wheat
          </option>

          <option value="Tomato">
            🍅 Tomato
          </option>

          <option value="Maize">
            🌽 Maize
          </option>

          <option value="Potato">
            🥔 Potato
          </option>

        </select>

      </section>


      {/* ==================================================
          CURRENT FARM CONDITIONS
      ================================================== */}

      <section>

        <div className="section-heading">

          <div>

            <span className="section-label">
              LIVE MONITORING
            </span>

            <h2>
              Current Farm Conditions
            </h2>

          </div>


          <span className="live-badge">
            ● LIVE
          </span>

        </div>


        <div className="metric-grid">


          {/* TEMPERATURE */}

          <div className="metric-card temperature-card">

            <div className="metric-icon">
              🌡️
            </div>

            <div>

              <span className="metric-label">
                Temperature
              </span>

              <div className="metric-value">

                {latestReading
                  ? latestReading.temperature
                  : "--"}

                <span>
                  °C
                </span>

              </div>

            </div>

          </div>


          {/* HUMIDITY */}

          <div className="metric-card humidity-card">

            <div className="metric-icon">
              💧
            </div>

            <div>

              <span className="metric-label">
                Humidity
              </span>

              <div className="metric-value">

                {latestReading
                  ? latestReading.humidity
                  : "--"}

                <span>
                  %
                </span>

              </div>

            </div>

          </div>


          {/* SOIL */}

          <div className="metric-card soil-card">

            <div className="metric-icon">
              🌱
            </div>

            <div>

              <span className="metric-label">
                Soil Moisture
              </span>

              <div className="metric-value">

                {latestReading
                  ? latestReading.soil_moisture
                  : "--"}

                <span>
                  %
                </span>

              </div>

            </div>

          </div>


          {/* WEATHER SUMMARY */}

          <div className="metric-card weather-summary-card">

            <div className="metric-icon">
              ☁️
            </div>

            <div>

              <span className="metric-label">
                Weather
              </span>

              <div className="weather-summary">
                Jaipur
              </div>

              <small>
                {weather?.current?.temperature_2m ?? "--"}°C
                {" | "}
                {analysis?.rain_probability ?? "--"}% rain
              </small>

            </div>

          </div>

        </div>

      </section>


      {/* ==================================================
          WEATHER + AGRICULTURE QUICK VIEW
      ================================================== */}

      <div className="two-column-grid">


        {/* ==================================================
            JAIPUR WEATHER
        ================================================== */}

        <section className="panel weather-panel">

          <div className="panel-header">

            <div>

              <span className="section-label">
                WEATHER INTELLIGENCE
              </span>

              <h2>
                🌤️ Jaipur Weather
              </h2>

            </div>

            <span className="location-badge">
              📍 Jaipur, Rajasthan
            </span>

          </div>


          <div className="weather-main">

            <div className="weather-big-icon">
              ☀️
            </div>

            <div>

              <span className="weather-condition">
                Current Conditions
              </span>

              <strong>
                {weather?.current?.temperature_2m ?? "--"}
                °C
              </strong>

              <p>
                Current temperature
              </p>

            </div>

          </div>


          <div className="weather-details">

            <div>

              <span>
                💧 Humidity
              </span>

              <strong>
                {weather?.current?.relative_humidity_2m ?? "--"}%
              </strong>

            </div>


            <div>

              <span>
                🌧️ Precipitation
              </span>

              <strong>
                {weather?.current?.precipitation ?? "--"} mm
              </strong>

            </div>


            <div>

              <span>
                ☔ Rain Probability
              </span>

              <strong>
                {analysis?.rain_probability ?? "--"}%
              </strong>

            </div>

          </div>

        </section>


        {/* ==================================================
            AGRICULTURE ANALYSIS
        ================================================== */}

        <section className="panel agriculture-panel">

          <div className="panel-header">

            <div>

              <span className="section-label">
                DECISION ENGINE
              </span>

              <h2>
                🌿 Agriculture Analysis
              </h2>

            </div>

            <span className="crop-badge">
              🌾 {crop}
            </span>

          </div>


          {analysis && (

            <div className="analysis-summary">


              {/* HEALTH */}

              <div className="analysis-row">

                <div className="analysis-icon health">
                  🌿
                </div>

                <div className="analysis-info">

                  <span>
                    Crop Health
                  </span>

                  <strong
                    className={
                      analysis.health_score < 60
                        ? "danger-text"
                        : "good-text"
                    }
                  >
                    {analysis.overall_status}
                  </strong>

                  <p>
                    Health Score:{" "}
                    {analysis.health_score}/100
                  </p>

                </div>

              </div>


              {/* IRRIGATION */}

              <div className="analysis-row">

                <div className="analysis-icon water">
                  💧
                </div>

                <div className="analysis-info">

                  <span>
                    Irrigation Status
                  </span>

                  <strong>
                    {analysis.irrigation_status}
                  </strong>

                  <p>
                    Priority:{" "}
                    {analysis.irrigation_level}
                  </p>

                </div>

              </div>


              {/* RECOMMENDATION */}

              <div className="analysis-row">

                <div className="analysis-icon recommendation">
                  💡
                </div>

                <div className="analysis-info">

                  <span>
                    Key Recommendation
                  </span>

                  <p className="recommendation-text">
                    {analysis.recommendation}
                  </p>

                </div>

              </div>

            </div>

          )}

        </section>

      </div>


      {/* ==================================================
          SENSOR HISTORY
      ================================================== */}

      <section className="panel chart-panel">

        <div className="panel-header">

          <div>

            <span className="section-label">
              DATA ANALYTICS
            </span>

            <h2>
              📊 Sensor History
            </h2>

          </div>

          <div className="chart-period">
            LIVE
          </div>

        </div>


        <div className="chart-container">

          <ResponsiveContainer
            width="100%"
            height={380}
          >

            <LineChart data={chartData}>

              <CartesianGrid
                strokeDasharray="3 3"
                opacity={0.15}
              />

              <XAxis
                dataKey="name"
                tick={{ fontSize: 12 }}
              />

              <YAxis
                domain={[0, 100]}
                tick={{ fontSize: 12 }}
              />

              <Tooltip />


              {/* TEMPERATURE */}

              <Line
                type="monotone"
                dataKey="temperature"
                name="Temperature"
                stroke="#ff9f43"
                strokeWidth={3}
                dot={false}
                activeDot={{ r: 6 }}
              />


              {/* HUMIDITY */}

              <Line
                type="monotone"
                dataKey="humidity"
                name="Humidity"
                stroke="#2196f3"
                strokeWidth={3}
                dot={false}
                activeDot={{ r: 6 }}
              />


              {/* SOIL */}

              <Line
                type="monotone"
                dataKey="soil"
                name="Soil Moisture"
                stroke="#2ecc71"
                strokeWidth={3}
                dot={false}
                activeDot={{ r: 6 }}
              />

            </LineChart>

          </ResponsiveContainer>

        </div>


        <div className="chart-legend">

          <span>
            <i className="legend-temp"></i>
            Temperature (°C)
          </span>

          <span>
            <i className="legend-humidity"></i>
            Humidity (%)
          </span>

          <span>
            <i className="legend-soil"></i>
            Soil Moisture (%)
          </span>

        </div>

      </section>


      {/* ==================================================
          ALERT CENTER + RECENT READINGS
      ================================================== */}

      <div className="two-column-grid">


        {/* ==================================================
            ALERT CENTER
        ================================================== */}

        <section className="panel alerts-panel">

          <div className="panel-header">

            <div>

              <span className="section-label">
                SAFETY MONITORING
              </span>

              <h2>
                🚨 Alert Center
              </h2>

            </div>


            <span
              className={
                totalAlerts > 0
                  ? "alert-count active"
                  : "alert-count"
              }
            >
              {totalAlerts > 0
                ? `${totalAlerts} Active Alerts`
                : "All Clear"}
            </span>

          </div>


          <div className="alert-list">


            {/* ISSUES */}

            {analysis?.issues?.map(
              (issue, index) => (

                <div
                  className="alert-item critical-alert"
                  key={`issue-${index}`}
                >

                  <div className="alert-item-icon">
                    🚨
                  </div>

                  <div>

                    <strong>
                      Critical Condition
                    </strong>

                    <p>
                      {issue}
                    </p>

                  </div>

                </div>

              )
            )}


            {/* WARNINGS */}

            {analysis?.warnings?.map(
              (warning, index) => (

                <div
                  className="alert-item warning-alert"
                  key={`warning-${index}`}
                >

                  <div className="alert-item-icon">
                    ⚠️
                  </div>

                  <div>

                    <strong>
                      Weather / Environment Warning
                    </strong>

                    <p>
                      {warning}
                    </p>

                  </div>

                </div>

              )
            )}


            {/* NORMAL */}

            {totalAlerts === 0 && (

              <div className="alert-item normal-alert">

                <div className="alert-item-icon">
                  ✅
                </div>

                <div>

                  <strong>
                    Farm Conditions Normal
                  </strong>

                  <p>
                    No major environmental issues detected.
                  </p>

                </div>

              </div>

            )}

          </div>

        </section>


        {/* ==================================================
            RECENT SENSOR READINGS
        ================================================== */}

        <section className="panel table-panel">

          <div className="panel-header">

            <div>

              <span className="section-label">
                LIVE DATA LOG
              </span>

              <h2>
                📋 Recent Sensor Readings
              </h2>

            </div>

            <span className="view-badge">
              LIVE
            </span>

          </div>


          <div className="table-wrapper">

            <table>

              <thead>

                <tr>

                  <th>
                    ID
                  </th>

                  <th>
                    Temperature
                  </th>

                  <th>
                    Humidity
                  </th>

                  <th>
                    Soil Moisture
                  </th>

                  <th>
                    Time
                  </th>

                </tr>

              </thead>


              <tbody>

                {sensorData
                  .slice(-8)
                  .reverse()
                  .map((reading) => (

                    <tr key={reading.id}>

                      <td>
                        #{reading.id}
                      </td>

                      <td>
                        {reading.temperature} °C
                      </td>

                      <td>
                        {reading.humidity} %
                      </td>

                      <td>
                        {reading.soil_moisture} %
                      </td>

                      <td>
                        {new Date(
                          reading.timestamp
                        ).toLocaleTimeString()}
                      </td>

                    </tr>

                  ))}

              </tbody>

            </table>

          </div>

        </section>

      </div>


      {/* ==================================================
          AI ASSISTANT
      ================================================== */}

      <section className="ai-section">

        <div className="ai-header">

          <div className="ai-title">

            <div className="ai-icon">
              🧠
            </div>

            <div>

              <span className="section-label">
                MULTIMODAL AI
              </span>

              <h2>
                AI Agricultural Assistant
              </h2>

              <p>
                Ask farming questions, get crop advice,
                or discuss current agricultural conditions.
              </p>

            </div>

          </div>


          <span className="ai-online">
            ● AI Online
          </span>

        </div>


        <div className="ai-input-area">

          <input
            type="text"
            placeholder="Ask me anything about farming, crops, weather, or agriculture..."
            value={question}
            onChange={(event) =>
              setQuestion(event.target.value)
            }
            onKeyDown={(event) => {

              if (
                event.key === "Enter" &&
                question.trim() &&
                !aiLoading
              ) {

                fetchAIAdvice(
                  crop,
                  question
                );

              }

            }}
          />


          <button
            onClick={() =>
              fetchAIAdvice(
                crop,
                question
              )
            }
            disabled={
              !question.trim() ||
              aiLoading
            }
          >

            {aiLoading
              ? "Thinking..."
              : "Send ✈"}

          </button>

        </div>


        {/* QUICK PROMPTS */}

        <div className="quick-prompts">

          <span>
            Quick questions:
          </span>

          <button
            onClick={() =>
              setQuestion(
                `Should I irrigate my ${crop} crop right now?`
              )
            }
          >
            Best time to irrigate?
          </button>

          <button
            onClick={() =>
              setQuestion(
                `What is the current health of my ${crop} crop?`
              )
            }
          >
            Crop health tips
          </button>

          <button
            onClick={() =>
              setQuestion(
                `How is the current weather affecting my ${crop} crop?`
              )
            }
          >
            Weather impact?
          </button>

        </div>


        {/* AI RESPONSE */}

        {aiLoading && (

          <div className="ai-loading">

            <span>
              🤖
            </span>

            AI is analyzing your farm conditions...

          </div>

        )}


        {aiAdvice && !aiLoading && (

          <div className="ai-response">

            <div className="response-header">

              <span>
                💡 AI Recommendation
              </span>

              <span className="response-crop">
                {crop}
              </span>

            </div>


            <div className="ai-content">

              {formatAIText(aiAdvice)}

            </div>

          </div>

        )}

      </section>


      {/* ==================================================
          FOOTER
      ================================================== */}

      <footer>

        <div className="footer-brand">

          <img
            src="/qubitscrew.png"
            alt="QubitsCrew"
          />

          <div>
            <strong>
              QubitsCrew
            </strong>

            <span>
              Built for a Greener, Smarter Tomorrow
            </span>
          </div>

        </div>


        <div className="footer-right">

          Smart Agriculture
          <span>•</span>
          QubitsCrew
          <span>•</span>
          2026

        </div>

      </footer>

    </div>

  );

}


export default App;