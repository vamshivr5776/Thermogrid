import { useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import "./App.css";

function App() {
  const [loadProfile, setLoadProfile] = useState(
    "0.4,0.6,0.8,1.0,1.2,1.0,0.7"
  );

  const [ambientProfile, setAmbientProfile] = useState(
    "30,30,31,31,32,32,31"
  );

  const [dtHours, setDtHours] = useState(1);

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function runSimulation() {
    setLoading(true);
    setError("");

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/thermal/simulate",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            load_profile: loadProfile.split(",").map(Number),
            ambient_profile: ambientProfile.split(",").map(Number),
            dt_hours: Number(dtHours),
          }),
        }
      );

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || "Simulation failed");
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  const maxLoad = result
    ? Math.max(...result.thermal_response.map((row) => row.load_pu))
    : 0;

  const hotspot = result?.summary.peak_hotspot_C ?? 0;

  let risk = "NORMAL";

  if (hotspot >= 110) {
    risk = "CRITICAL";
  } else if (hotspot >= 100) {
    risk = "WARNING";
  }

  return (
    <div className="app">

      {/* HEADER */}
      <header className="header">
        <div>
          <h1>ThermoGrid</h1>
          <p>Transformer Thermal Intelligence</p>
        </div>

        <div className="system-status">
          <span className="status-dot"></span>
          API Connected
        </div>
      </header>

      <main>

        {/* INPUT PANEL */}
        <section className="panel">

          <div className="section-title">
            <h2>Thermal Simulation</h2>
            <p>Configure transformer operating conditions</p>
          </div>

          <div className="inputs">

            <div className="input-group">
              <label>Load Profile (pu)</label>

              <input
                value={loadProfile}
                onChange={(e) => setLoadProfile(e.target.value)}
                placeholder="0.4,0.6,0.8,1.0..."
              />
            </div>

            <div className="input-group">
              <label>Ambient Temperature (°C)</label>

              <input
                value={ambientProfile}
                onChange={(e) => setAmbientProfile(e.target.value)}
                placeholder="30,30,31,31..."
              />
            </div>

            <div className="input-group small">
              <label>Time Step (hours)</label>

              <input
                type="number"
                min="0.1"
                step="0.1"
                value={dtHours}
                onChange={(e) => setDtHours(e.target.value)}
              />
            </div>

            <button
              className="simulate-button"
              onClick={runSimulation}
              disabled={loading}
            >
              {loading ? "Running..." : "Run Simulation"}
            </button>

          </div>

          {error && <div className="error">{error}</div>}

        </section>

        {/* RESULTS */}
        {result && (
          <>

            {/* KPI CARDS */}
            <section className="kpi-grid">

              <div className="kpi-card">
                <span>Peak Hotspot</span>
                <strong>{hotspot.toFixed(2)}°C</strong>
                <small>Maximum winding temperature</small>
              </div>

              <div className="kpi-card">
                <span>Peak Top-Oil</span>
                <strong>
                  {result.summary.peak_top_oil_C.toFixed(2)}°C
                </strong>
                <small>Maximum top-oil temperature</small>
              </div>

              <div className="kpi-card">
                <span>Aging Factor</span>
                <strong>
                  {result.summary.peak_aging_factor.toFixed(3)}×
                </strong>
                <small>Thermal aging acceleration</small>
              </div>

              <div className="kpi-card">
                <span>Maximum Load</span>
                <strong>{maxLoad.toFixed(2)} pu</strong>
                <small>Highest simulated loading</small>
              </div>

            </section>

            {/* RISK */}
            <section className={`risk-card ${risk.toLowerCase()}`}>
              <div>
                <span>THERMAL STATUS</span>
                <strong>{risk}</strong>
              </div>

              <p>
                Peak hotspot temperature:{" "}
                <b>{hotspot.toFixed(2)}°C</b>
              </p>
            </section>

            {/* THERMAL CHART */}
            <section className="panel chart-panel">

              <div className="section-title">
                <h2>Thermal Response</h2>
                <p>Temperature evolution over the simulation period</p>
              </div>

              <div className="chart">
                <ResponsiveContainer width="100%" height={380}>
                  <LineChart data={result.thermal_response}>

                    <CartesianGrid strokeDasharray="3 3" />

                    <XAxis
                      dataKey="time_hr"
                      label={{
                        value: "Time (hours)",
                        position: "insideBottom",
                        offset: -5,
                      }}
                    />

                    <YAxis
                      label={{
                        value: "Temperature (°C)",
                        angle: -90,
                        position: "insideLeft",
                      }}
                    />

                    <Tooltip />

                    <Legend />

                    <Line
                      type="monotone"
                      dataKey="ambient_C"
                      name="Ambient"
                      stroke="#64748b"
                      strokeWidth={2}
                      dot={false}
                    />

                    <Line
                      type="monotone"
                      dataKey="top_oil_C"
                      name="Top-Oil"
                      stroke="#2563eb"
                      strokeWidth={3}
                      dot={false}
                    />

                    <Line
                      type="monotone"
                      dataKey="hotspot_C"
                      name="Hotspot"
                      stroke="#dc2626"
                      strokeWidth={3}
                      dot={false}
                    />

                  </LineChart>
                </ResponsiveContainer>
              </div>

            </section>

            {/* LOAD CHART */}
            <section className="panel chart-panel">

              <div className="section-title">
                <h2>Load Profile</h2>
                <p>Transformer loading throughout the simulation</p>
              </div>

              <div className="chart">

                <ResponsiveContainer width="100%" height={300}>

                  <LineChart data={result.thermal_response}>

                    <CartesianGrid strokeDasharray="3 3" />

                    <XAxis dataKey="time_hr" />

                    <YAxis
                      label={{
                        value: "Load (pu)",
                        angle: -90,
                        position: "insideLeft",
                      }}
                    />

                    <Tooltip />

                    <Line
                      type="monotone"
                      dataKey="load_pu"
                      name="Load"
                      stroke="#7c3aed"
                      strokeWidth={3}
                    />

                  </LineChart>

                </ResponsiveContainer>

              </div>

            </section>

          </>
        )}

      </main>

      <footer>
        ThermoGrid • Transformer Thermal Analysis Engine
      </footer>

    </div>
  );
}

export default App;