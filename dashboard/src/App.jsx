import { useEffect, useState } from "react";
import {
  MapContainer,
  TileLayer,
  Polygon,
  CircleMarker,
  Popup,
  useMap,
} from "react-leaflet";
import "leaflet/dist/leaflet.css";
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

// ---------------------------------------------------------
// Default AOI
// ---------------------------------------------------------
// Current test region around Phoenix, Arizona.
// Later this should become dynamically generated from
// the transformer coordinates.
// ---------------------------------------------------------

const DEFAULT_AOI = {
  type: "Polygon",
  coordinates: [[
    [-112.10, 33.40],
    [-112.05, 33.40],
    [-112.05, 33.50],
    [-112.10, 33.50],
    [-112.10, 33.40],
  ]],
};

const API_URL = "http://127.0.0.1:8000";


// ---------------------------------------------------------
// Verification map
// ---------------------------------------------------------
// This is a visualization layer only. It does not change the
// ThermoGrid analysis request or backend logic.
//
// The current backend response contains the mapped tile ID,
// temperature, mapping method and distance, but not the full
// FortyGuard tile geometries. Therefore this map shows:
//   1. The ThermoGrid AOI
//   2. The transformer coordinate
//   3. The temperature returned by SpatialMapper
//   4. The selected tile ID / mapping method
//
// Actual FortyGuard heatmap tile polygons can only be drawn
// after the backend exposes their geometries in its response.

function MapViewport({ transformer, aoi }) {
  const map = useMap();

  useEffect(() => {
    if (!transformer || !aoi?.length) return;

    const points = [
      ...aoi,
      transformer,
    ];

    const bounds = points.map(
      ([lat, lon]) => [lat, lon]
    );

    map.fitBounds(bounds, {
      padding: [35, 35],
      maxZoom: 13,
    });
  }, [map, transformer, aoi]);

  return null;
}

function App() {
  // -------------------------------------------------------
  // API status
  // -------------------------------------------------------

  const [apiConnected, setApiConnected] = useState(false);

  useEffect(() => {
    let cancelled = false;

    async function checkApiHealth() {
      try {
        const response = await fetch(
          `${API_URL}/health`
        );

        if (!cancelled) {
          setApiConnected(response.ok);
        }
      } catch {
        if (!cancelled) {
          setApiConnected(false);
        }
      }
    }

    checkApiHealth();

    const interval = setInterval(
      checkApiHealth,
      10000
    );

    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, []);

  // -------------------------------------------------------
  // Transformer location
  // -------------------------------------------------------

  const [latitude, setLatitude] =
    useState("33.4484");

  const [longitude, setLongitude] =
    useState("-112.0740");

  // -------------------------------------------------------
  // FortyGuard analysis
  // -------------------------------------------------------

  const getTodayLocalISO = () => {
    const now = new Date();
    const offset = now.getTimezoneOffset();
    return new Date(now.getTime() - offset * 60000)
      .toISOString()
      .slice(0, 10);
  };

  const [startDate, setStartDate] =
    useState(getTodayLocalISO);

  const [startTime, setStartTime] =
    useState("12:00");

  const [granularity, setGranularity] =
    useState(100);

  // -------------------------------------------------------
  // Transformer loading
  // -------------------------------------------------------

  const [loadProfile, setLoadProfile] =
    useState(
      "0.5,0.6,0.7,0.8,0.9,1.0"
    );

  const [dtHours, setDtHours] =
    useState(1);

  // -------------------------------------------------------
  // Application state
  // -------------------------------------------------------

  const [result, setResult] =
    useState(null);

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");

  // -------------------------------------------------------
  // Live analysis timer
  // -------------------------------------------------------

  const [elapsedMs, setElapsedMs] =
    useState(0);

  useEffect(() => {
    if (!loading) {
      return undefined;
    }

    const startedAt = performance.now();

    const timer = setInterval(() => {
      setElapsedMs(performance.now() - startedAt);
    }, 100);

    return () => clearInterval(timer);
  }, [loading]);

  const elapsedSeconds =
    (elapsedMs / 1000).toFixed(1);

  // -------------------------------------------------------
  // Run complete ThermoGrid analysis
  // -------------------------------------------------------

  async function runAnalysis() {
    setLoading(true);
    setElapsedMs(0);
    setError("");
    setResult(null);

    try {
      // ---------------------------------------------------
      // Parse numeric inputs
      // ---------------------------------------------------

      const lat = Number(latitude);
      const lon = Number(longitude);
      const dt = Number(dtHours);
      const gran = Number(granularity);

      // ---------------------------------------------------
      // Validate latitude
      // ---------------------------------------------------

      if (
        !Number.isFinite(lat) ||
        lat < -90 ||
        lat > 90
      ) {
        throw new Error(
          "Latitude must be between -90 and 90."
        );
      }

      // ---------------------------------------------------
      // Validate longitude
      // ---------------------------------------------------

      if (
        !Number.isFinite(lon) ||
        lon < -180 ||
        lon > 180
      ) {
        throw new Error(
          "Longitude must be between -180 and 180."
        );
      }

      // ---------------------------------------------------
      // Validate time step
      // ---------------------------------------------------

      if (
        !Number.isFinite(dt) ||
        dt <= 0
      ) {
        throw new Error(
          "Time step must be greater than 0 hours."
        );
      }

      // ---------------------------------------------------
      // Validate granularity
      // ---------------------------------------------------

      if (
        !Number.isFinite(gran) ||
        gran <= 0
      ) {
        throw new Error(
          "Granularity must be greater than 0."
        );
      }

      // ---------------------------------------------------
      // Parse load profile
      // ---------------------------------------------------

      const parsedLoadProfile = loadProfile
        .split(",")
        .map((value) => value.trim())
        .filter((value) => value !== "")
        .map(Number);

      // ---------------------------------------------------
      // Validate load profile
      // ---------------------------------------------------

      if (parsedLoadProfile.length === 0) {
        throw new Error(
          "Enter at least one load value."
        );
      }

      if (
        parsedLoadProfile.some(
          (value) => !Number.isFinite(value)
        )
      ) {
        throw new Error(
          "Load profile must contain only valid numbers separated by commas."
        );
      }

      if (
        parsedLoadProfile.some(
          (value) => value < 0
        )
      ) {
        throw new Error(
          "Load profile cannot contain negative values."
        );
      }

      // ---------------------------------------------------
      // Validate date
      // ---------------------------------------------------

      if (!startDate) {
        throw new Error(
          "Please select an analysis date."
        );
      }

      // ---------------------------------------------------
      // Validate time
      // ---------------------------------------------------

      if (!startTime) {
        throw new Error(
          "Please select an analysis time."
        );
      }

      // ---------------------------------------------------
      // Check backend availability
      // ---------------------------------------------------

      if (!apiConnected) {
        throw new Error(
          "ThermoGrid API is not connected. Make sure the FastAPI server is running."
        );
      }

      // ---------------------------------------------------
      // Send analysis request
      // ---------------------------------------------------

      const response = await fetch(
        `${API_URL}/analysis/transformer`,
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json",
          },

          body: JSON.stringify({
            latitude: lat,
            longitude: lon,

            polygon_aoi: DEFAULT_AOI,

            start_date: startDate,
            start_time: startTime,

            load_profile:
              parsedLoadProfile,

            dt_hours: dt,
            granularity: gran,
          }),
        }
      );

      // ---------------------------------------------------
      // Parse server response safely
      // ---------------------------------------------------

      let data;

      try {
        data = await response.json();
      } catch {
        throw new Error(
          "ThermoGrid API returned an invalid response."
        );
      }

      // ---------------------------------------------------
      // Handle HTTP errors
      // ---------------------------------------------------

      if (!response.ok) {
        const serverMessage =
          typeof data?.detail === "string"
            ? data.detail
            : "";

        if (response.status === 400) {
          throw new Error(
            serverMessage ||
              "Invalid analysis request."
          );
        }

        if (response.status === 502) {
          throw new Error(
            serverMessage ||
              "FortyGuard service is unavailable."
          );
        }

        if (response.status === 504) {
          throw new Error(
            "FortyGuard analysis timed out. Try a smaller AOI or try again."
          );
        }

        throw new Error(
          serverMessage ||
            `ThermoGrid API returned HTTP ${response.status}.`
        );
      }

      // ---------------------------------------------------
      // Validate returned result
      // ---------------------------------------------------

      if (
        !data ||
        typeof data !== "object"
      ) {
        throw new Error(
          "ThermoGrid returned an empty analysis result."
        );
      }

      if (
        !data.environment ||
        !data.thermal ||
        !data.risk ||
        !data.thermal_response
      ) {
        throw new Error(
          "ThermoGrid returned an incomplete analysis result."
        );
      }

      setResult(data);

    } catch (err) {
      console.error(
        "ThermoGrid analysis error:",
        err
      );

      if (
        err instanceof TypeError &&
        err.message === "Failed to fetch"
      ) {
        setError(
          "Unable to reach the ThermoGrid API. Make sure the FastAPI server is running."
        );
      } else {
        setError(
          err instanceof Error
            ? err.message
            : "An unexpected error occurred."
        );
      }

    } finally {
      setLoading(false);
    }
  }

  // -------------------------------------------------------
  // Derived values
  // -------------------------------------------------------

  const hotspot =
    result?.thermal?.peak_hotspot_C ?? 0;

  const topOil =
    result?.thermal?.peak_top_oil_C ?? 0;

  const aging =
    result?.thermal?.peak_aging_factor ?? 0;

  const environment =
    result?.environment?.temperature_C ?? 0;

  const maxLoad =
    result?.thermal_response?.length
      ? Math.max(
          ...result.thermal_response.map(
            (row) => row.load_pu
          )
        )
      : 0;

  // -------------------------------------------------------
  // Risk comes ONLY from backend
  // -------------------------------------------------------

  const riskLevel =
    result?.risk?.level ?? "UNKNOWN";

  const riskClass =
    riskLevel.toLowerCase();

  // -------------------------------------------------------
  // Map verification values
  // -------------------------------------------------------

  const transformerLat = Number(latitude);
  const transformerLon = Number(longitude);

  const validTransformerCoordinates =
    Number.isFinite(transformerLat) &&
    Number.isFinite(transformerLon) &&
    transformerLat >= -90 &&
    transformerLat <= 90 &&
    transformerLon >= -180 &&
    transformerLon <= 180;

  const aoiPositions =
    DEFAULT_AOI.coordinates[0].map(
      ([lon, lat]) => [lat, lon]
    );

  const mapCenter = validTransformerCoordinates
    ? [transformerLat, transformerLon]
    : [33.4484, -112.0740];

  // -------------------------------------------------------
  // Render
  // -------------------------------------------------------

  return (
    <div className="app">

      {/* =================================================
          HEADER
      ================================================= */}

      <style>{`
        @keyframes thermoGridSpin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }

        @keyframes thermoGridSpinReverse {
          from { transform: rotate(360deg); }
          to { transform: rotate(0deg); }
        }

        @keyframes thermoGridPulse {
          0%, 100% {
            transform: scale(0.8);
            opacity: 0.65;
          }
          50% {
            transform: scale(1.35);
            opacity: 1;
          }
        }

        @keyframes thermoGridScan {
          0% { transform: translateX(-120%); opacity: 0; }
          15% { opacity: 1; }
          85% { opacity: 1; }
          100% { transform: translateX(120%); opacity: 0; }
        }
      `}</style>

      <header
        className="header"
        style={{
          position: "relative",
          overflow: "hidden",
        }}
      >

        <div>
          <div
            aria-hidden="true"
            style={{
              fontSize: "11px",
              letterSpacing: "2px",
              textTransform: "uppercase",
              opacity: 0.6,
              marginBottom: "6px",
            }}
          >
            ⚡ GRID INTELLIGENCE / THERMAL SYSTEM
          </div>

          <h1>ThermoGrid</h1>

          <p>
            Transformer Thermal Intelligence
          </p>
        </div>

        <div
          aria-hidden="true"
          style={{
            position: "absolute",
            right: "150px",
            top: "50%",
            transform: "translateY(-50%)",
            width: "92px",
            height: "92px",
            opacity: 0.8,
            pointerEvents: "none",
          }}
        >
          <div
            style={{
              position: "absolute",
              inset: 0,
              border: "1px solid rgba(56,189,248,0.3)",
              borderRadius: "50%",
              animation:
                "thermoGridSpin 10s linear infinite",
            }}
          />

          <div
            style={{
              position: "absolute",
              inset: "13px",
              border: "1px dashed rgba(45,212,191,0.35)",
              borderRadius: "50%",
              animation:
                "thermoGridSpinReverse 7s linear infinite",
            }}
          />

          <svg
            viewBox="0 0 92 92"
            width="92"
            height="92"
            style={{
              position: "absolute",
              inset: 0,
            }}
          >
            <path
              d="M18 25 H34 M58 25 H74 M18 67 H34 M58 67 H74"
              stroke="rgba(56,189,248,0.65)"
              strokeWidth="2"
              fill="none"
            />
            <path
              d="M31 18 C22 25 22 34 31 41 C40 48 40 57 31 64 C22 71 22 78 31 84"
              stroke="#38bdf8"
              strokeWidth="3"
              fill="none"
            />
            <path
              d="M61 18 C52 25 52 34 61 41 C70 48 70 57 61 64 C52 71 52 78 61 84"
              stroke="#2dd4bf"
              strokeWidth="3"
              fill="none"
            />
          </svg>

          <span
            style={{
              position: "absolute",
              left: "50%",
              top: "50%",
              width: "7px",
              height: "7px",
              borderRadius: "50%",
              background: "#67e8f9",
              boxShadow:
                "0 0 10px #22d3ee, 0 0 22px rgba(34,211,238,0.7)",
              animation:
                "thermoGridPulse 1.5s ease-in-out infinite",
            }}
          />
        </div>

        <div className="system-status">

          <span
            className={`status-dot ${
              apiConnected
                ? "connected"
                : "disconnected"
            }`}
          ></span>

          {apiConnected
            ? "API Connected"
            : "API Disconnected"}

        </div>

      </header>

      <main>

        {/* =================================================
            INPUT PANEL
        ================================================= */}

        <section
          className="panel"
          style={{
            position: "relative",
            overflow: "hidden",
          }}
        >

          <div
            aria-hidden="true"
            style={{
              position: "absolute",
              left: 0,
              right: 0,
              top: 0,
              height: "1px",
              background:
                "linear-gradient(90deg, transparent, rgba(34,211,238,0.5), transparent)",
              animation:
                "thermoGridScan 4s linear infinite",
            }}
          />

          <div className="section-title">

            <h2>
              Transformer Analysis
            </h2>

            <p>
              Analyze transformer thermal behaviour
              using real FortyGuard environmental data.
            </p>

          </div>

          <div className="inputs">

            {/* Latitude */}

            <div className="input-group">

              <label>
                Transformer Latitude
              </label>

              <input
                type="number"
                step="0.000001"
                value={latitude}
                onChange={(e) =>
                  setLatitude(e.target.value)
                }
              />

            </div>

            {/* Longitude */}

            <div className="input-group">

              <label>
                Transformer Longitude
              </label>

              <input
                type="number"
                step="0.000001"
                value={longitude}
                onChange={(e) =>
                  setLongitude(e.target.value)
                }
              />

            </div>

            {/* Date */}

            <div className="input-group">

              <label>
                Analysis Date
              </label>

              <input
                type="date"
                value={startDate}
                onChange={(e) =>
                  setStartDate(e.target.value)
                }
              />

            </div>

            {/* Time */}

            <div className="input-group">

              <label>
                Analysis Time
                <span
                  style={{
                    marginLeft: "8px",
                    opacity: 0.65,
                    fontSize: "11px",
                  }}
                >
                  ({(() => {
                    const [hours, minutes] =
                      startTime.split(":").map(Number);

                    if (
                      !Number.isFinite(hours) ||
                      !Number.isFinite(minutes)
                    ) {
                      return startTime;
                    }

                    const period =
                      hours >= 12 ? "PM" : "AM";

                    const displayHour =
                      hours % 12 || 12;

                    return `${String(displayHour).padStart(2, "0")}:${String(minutes).padStart(2, "0")} ${period}`;
                  })()})
                </span>
              </label>

              <input
                type="time"
                value={startTime}
                onChange={(e) =>
                  setStartTime(e.target.value)
                }
              />

            </div>

            {/* Load */}

            <div className="input-group">

              <label>
                Load Profile (pu)
              </label>

              <input
                value={loadProfile}
                onChange={(e) =>
                  setLoadProfile(e.target.value)
                }
                placeholder="0.5,0.6,0.7,0.8,0.9,1.0"
              />

            </div>

            {/* Time step */}

            <div className="input-group small">

              <label>
                Time Step (hours)
              </label>

              <input
                type="number"
                min="0.1"
                step="0.1"
                value={dtHours}
                onChange={(e) =>
                  setDtHours(e.target.value)
                }
              />

            </div>

            {/* Granularity */}

            <div className="input-group small">

              <label>
                FortyGuard Granularity
              </label>

              <input
                type="number"
                min="1"
                value={granularity}
                onChange={(e) =>
                  setGranularity(e.target.value)
                }
              />

            </div>

            {/* Run */}

            <button
              className="simulate-button"
              onClick={runAnalysis}
              disabled={loading}
            >
              {loading
                ? `Analyzing... ${elapsedSeconds}s`
                : "Run ThermoGrid Analysis"}
            </button>

          </div>

          {/* Live analysis status */}
          {loading && (
            <div
              style={{
                marginTop: "18px",
                padding: "12px 16px",
                borderRadius: "12px",
                border: "1px solid rgba(34,211,238,0.25)",
                background:
                  "linear-gradient(90deg, rgba(8,47,73,0.22), rgba(15,23,42,0.3))",
                display: "flex",
                alignItems: "center",
                gap: "12px",
              }}
            >
              <span
                aria-hidden="true"
                style={{
                  width: "9px",
                  height: "9px",
                  borderRadius: "50%",
                  background: "#22d3ee",
                  boxShadow:
                    "0 0 12px rgba(34,211,238,0.9)",
                  animation:
                    "thermoGridPulse 1.2s ease-in-out infinite",
                }}
              />

              <div style={{ flex: 1 }}>
                <strong>
                  ThermoGrid analysis in progress
                </strong>

                <div
                  style={{
                    fontSize: "12px",
                    opacity: 0.7,
                    marginTop: "3px",
                  }}
                >
                  FortyGuard → spatial mapping → thermal model → risk engine
                </div>
              </div>

              <strong
                style={{
                  fontVariantNumeric: "tabular-nums",
                  color: "#67e8f9",
                  minWidth: "58px",
                  textAlign: "right",
                }}
              >
                {elapsedSeconds}s
              </strong>
            </div>
          )}

          {/* Error */}

          {error && (
            <div className="error">
              <strong>
                Analysis failed
              </strong>

              <p>
                {error}
              </p>

              <small>
                Failed after {elapsedSeconds}s
              </small>
            </div>
          )}

          {!loading && result && (
            <div
              style={{
                marginTop: "14px",
                fontSize: "12px",
                opacity: 0.7,
              }}
            >
              ✓ Analysis completed in{" "}
              <strong>{elapsedSeconds}s</strong>
            </div>
          )}

        </section>

        {/* =================================================
            LOCATION / AOI VERIFICATION MAP
        ================================================= */}

        <section
          className="panel"
          style={{
            marginTop: "24px",
            overflow: "hidden",
          }}
        >
          <div className="section-title">
            <h2>
              AOI & Transformer Verification
            </h2>

            <p>
              Visual check of the Phoenix AOI and the exact
              transformer coordinate sent to FortyGuard.
            </p>
          </div>

          <div
            style={{
              border: "1px solid rgba(148,163,184,0.25)",
              borderRadius: "16px",
              overflow: "hidden",
              background: "#0f172a",
            }}
          >
            <MapContainer
              center={mapCenter}
              zoom={12}
              scrollWheelZoom={true}
              style={{
                width: "100%",
                height: "430px",
              }}
            >
              <TileLayer
                attribution='&copy; OpenStreetMap contributors'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              />

              <MapViewport
                transformer={
                  validTransformerCoordinates
                    ? [transformerLat, transformerLon]
                    : null
                }
                aoi={aoiPositions}
              />

              <Polygon
                positions={aoiPositions}
                pathOptions={{
                  color: "#22d3ee",
                  weight: 3,
                  fillColor: "#06b6d4",
                  fillOpacity: 0.12,
                }}
              >
                <Popup>
                  <strong>ThermoGrid AOI</strong>
                  <br />
                  Phoenix, Arizona
                  <br />
                  Default analysis polygon
                </Popup>
              </Polygon>

              {validTransformerCoordinates && (
                <CircleMarker
                  center={[
                    transformerLat,
                    transformerLon,
                  ]}
                  radius={10}
                  pathOptions={{
                    color: "#ffffff",
                    weight: 3,
                    fillColor: "#ef4444",
                    fillOpacity: 1,
                  }}
                >
                  <Popup>
                    <strong>Transformer</strong>
                    <br />
                    Latitude:{" "}
                    {transformerLat.toFixed(6)}
                    <br />
                    Longitude:{" "}
                    {transformerLon.toFixed(6)}

                    {result?.environment && (
                      <>
                        <br />
                        <br />
                        <strong>
                          Mapped temperature:
                        </strong>{" "}
                        {Number(
                          result.environment.temperature_C
                        ).toFixed(2)}
                        °C
                        <br />
                        <strong>
                          Tile:
                        </strong>{" "}
                        {result.environment.tile_id}
                        <br />
                        <strong>
                          Method:
                        </strong>{" "}
                        {result.environment.mapping_method}
                        <br />
                        <strong>
                          Distance:
                        </strong>{" "}
                        {Number(
                          result.environment.distance_km
                        ).toFixed(3)}
                        {" "}km
                      </>
                    )}
                  </Popup>
                </CircleMarker>
              )}
            </MapContainer>
          </div>

          <div
            style={{
              display: "grid",
              gridTemplateColumns:
                "repeat(auto-fit, minmax(180px, 1fr))",
              gap: "12px",
              marginTop: "14px",
            }}
          >
            <div
              style={{
                padding: "12px 14px",
                borderRadius: "12px",
                background:
                  "rgba(34,211,238,0.08)",
                border:
                  "1px solid rgba(34,211,238,0.18)",
              }}
            >
              <small>TRANSFORMER</small>
              <div
                style={{
                  marginTop: "4px",
                  fontWeight: 700,
                }}
              >
                {validTransformerCoordinates
                  ? `${transformerLat.toFixed(6)}, ${transformerLon.toFixed(6)}`
                  : "Invalid coordinates"}
              </div>
            </div>

            <div
              style={{
                padding: "12px 14px",
                borderRadius: "12px",
                background:
                  "rgba(59,130,246,0.08)",
                border:
                  "1px solid rgba(59,130,246,0.18)",
              }}
            >
              <small>AOI</small>
              <div
                style={{
                  marginTop: "4px",
                  fontWeight: 700,
                }}
              >
                −112.10 to −112.05° lon
                <br />
                33.40 to 33.50° lat
              </div>
            </div>

            <div
              style={{
                padding: "12px 14px",
                borderRadius: "12px",
                background:
                  "rgba(239,68,68,0.08)",
                border:
                  "1px solid rgba(239,68,68,0.18)",
              }}
            >
              <small>MAPPED ENVIRONMENT</small>
              <div
                style={{
                  marginTop: "4px",
                  fontWeight: 700,
                }}
              >
                {result?.environment
                  ? `${Number(
                      result.environment.temperature_C
                    ).toFixed(2)}°C`
                  : "Run analysis"}
              </div>
            </div>

            <div
              style={{
                padding: "12px 14px",
                borderRadius: "12px",
                background:
                  "rgba(168,85,247,0.08)",
                border:
                  "1px solid rgba(168,85,247,0.18)",
              }}
            >
              <small>MAPPING</small>
              <div
                style={{
                  marginTop: "4px",
                  fontWeight: 700,
                }}
              >
                {result?.environment
                  ? result.environment.mapping_method
                  : "Waiting for result"}
              </div>
            </div>
          </div>

          <div
            style={{
              marginTop: "12px",
              padding: "11px 14px",
              borderRadius: "10px",
              fontSize: "12px",
              lineHeight: 1.5,
              opacity: 0.72,
              border:
                "1px solid rgba(148,163,184,0.18)",
            }}
          >
            <strong>Verification note:</strong>{" "}
            the red marker is the transformer coordinate,
            while the cyan polygon is the AOI being sent in
            the existing analysis request. The temperature
            shown here is the value returned by
            <code> SpatialMapper </code>
            for that transformer. The current API response does
            not expose the individual FortyGuard tile geometries,
            so this map does not pretend to draw a heatmap that
            the backend has not returned.
          </div>
        </section>

        {/* =================================================
            RESULTS
        ================================================= */}

        {result && (
          <>

            {/* =================================================
                KPI CARDS
            ================================================= */}

            <section className="kpi-grid">

              <div className="kpi-card">

                <span>
                  Ambient Temperature
                </span>

                <strong>
                  {environment.toFixed(2)}°C
                </strong>

                <small>
                  FortyGuard mapped environment
                </small>

              </div>

              <div className="kpi-card">

                <span>
                  Peak Hotspot
                </span>

                <strong>
                  {hotspot.toFixed(2)}°C
                </strong>

                <small>
                  Maximum winding temperature
                </small>

              </div>

              <div className="kpi-card">

                <span>
                  Peak Top-Oil
                </span>

                <strong>
                  {topOil.toFixed(2)}°C
                </strong>

                <small>
                  Maximum top-oil temperature
                </small>

              </div>

              <div className="kpi-card">

                <span>
                  Aging Factor
                </span>

                <strong>
                  {aging.toFixed(3)}×
                </strong>

                <small>
                  Thermal aging acceleration
                </small>

              </div>

            </section>

            {/* =================================================
                ENVIRONMENT
            ================================================= */}

            <section className="panel">

              <div className="section-title">

                <h2>
                  Environmental Mapping
                </h2>

                <p>
                  FortyGuard → SpatialMapper
                </p>

              </div>

              <div className="kpi-grid">

                <div className="kpi-card">

                  <span>
                    Tile ID
                  </span>

                  <strong>
                    {result.environment.tile_id}
                  </strong>

                </div>

                <div className="kpi-card">

                  <span>
                    Mapping Method
                  </span>

                  <strong>
                    {result.environment.mapping_method}
                  </strong>

                </div>

                <div className="kpi-card">

                  <span>
                    Minimum Temperature
                  </span>

                  <strong>
                    {Number(
                      result.environment.minimum_C
                    ).toFixed(2)}°C
                  </strong>

                </div>

                <div className="kpi-card">

                  <span>
                    Maximum Temperature
                  </span>

                  <strong>
                    {Number(
                      result.environment.maximum_C
                    ).toFixed(2)}°C
                  </strong>

                </div>

              </div>

            </section>

            {/* =================================================
                RISK
            ================================================= */}

            <section
              className={`risk-card ${riskClass}`}
            >

              <div>

                <span>
                  THERMAL STATUS
                </span>

                <strong>
                  {riskLevel}
                </strong>

              </div>

              <p>

                {result.risk.message}

                <br />

                Peak hotspot:
                {" "}

                <b>
                  {Number(
                    result.risk.hotspot_temperature_C
                  ).toFixed(2)}°C
                </b>

                {" • "}

                Risk score:
                {" "}

                <b>
                  {Number(
                    result.risk.score
                  ).toFixed(2)}
                </b>

              </p>

            </section>

            {/* =================================================
                TRANSFORMER HEALTH
            ================================================= */}

            <section className="panel">

              <div className="section-title">

                <h2>
                  Transformer Health
                </h2>

                <p>
                  Thermal aging and life indicators
                </p>

              </div>

              <div className="kpi-grid">

                <div className="kpi-card">

                  <span>
                    Average Aging
                  </span>

                  <strong>
                    {Number(
                      result.thermal.average_aging_factor
                    ).toFixed(4)}×
                  </strong>

                </div>

                <div className="kpi-card">

                  <span>
                    Equivalent Aging
                  </span>

                  <strong>
                    {Number(
                      result.thermal.equivalent_aging_hours
                    ).toFixed(3)} h
                  </strong>

                </div>

                <div className="kpi-card">

                  <span>
                    Loss of Life
                  </span>

                  <strong>
                    {Number(
                      result.thermal.loss_of_life_percent
                    ).toFixed(6)}%
                  </strong>

                </div>

                <div className="kpi-card">

                  <span>
                    Maximum Load
                  </span>

                  <strong>
                    {maxLoad.toFixed(2)} pu
                  </strong>

                </div>

              </div>

            </section>

            {/* =================================================
                THERMAL CHART
            ================================================= */}

            <section className="panel chart-panel">

              <div className="section-title">

                <h2>
                  Thermal Response
                </h2>

                <p>
                  Ambient, top-oil and winding hotspot
                  temperature over time
                </p>

              </div>

              <div className="chart">

                <ResponsiveContainer
                  width="100%"
                  height={380}
                >

                  <LineChart
                    data={result.thermal_response}
                  >

                    <CartesianGrid
                      strokeDasharray="3 3"
                    />

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

            {/* =================================================
                LOAD CHART
            ================================================= */}

            <section className="panel chart-panel">

              <div className="section-title">

                <h2>
                  Load Profile
                </h2>

                <p>
                  Transformer loading throughout
                  the analysis period
                </p>

              </div>

              <div className="chart">

                <ResponsiveContainer
                  width="100%"
                  height={300}
                >

                  <LineChart
                    data={result.thermal_response}
                  >

                    <CartesianGrid
                      strokeDasharray="3 3"
                    />

                    <XAxis
                      dataKey="time_hr"
                    />

                    <YAxis
                      label={{
                        value: "Load (pu)",
                        angle: -90,
                        position: "insideLeft",
                      }}
                    />

                    <Tooltip />

                    <Legend />

                    <Line
                      type="monotone"
                      dataKey="load_pu"
                      name="Transformer Load"
                      stroke="#7c3aed"
                      strokeWidth={3}
                    />

                  </LineChart>

                </ResponsiveContainer>

              </div>

            </section>

            {/* =================================================
                FORTYGUARD DETAILS
            ================================================= */}

            <section className="panel">

              <div className="section-title">

                <h2>
                  FortyGuard Data
                </h2>

                <p>
                  Environmental heatmap information
                </p>

              </div>

              <p>
                Activity ID:
                {" "}

                <code>
                  {result.fortyguard.activity_id}
                </code>
              </p>

              <p>
                Tiles analyzed:
                {" "}

                <b>
                  {result.fortyguard.statistics.tile_count}
                </b>
              </p>

              <p>
                Regional minimum:
                {" "}

                <b>
                  {Number(
                    result.fortyguard.statistics.minimum_C
                  ).toFixed(2)}°C
                </b>
              </p>

              <p>
                Regional maximum:
                {" "}

                <b>
                  {Number(
                    result.fortyguard.statistics.maximum_C
                  ).toFixed(2)}°C
                </b>
              </p>

              <p>
                Regional mean:
                {" "}

                <b>
                  {Number(
                    result.fortyguard.statistics.mean_C
                  ).toFixed(2)}°C
                </b>
              </p>

            </section>

          </>
        )}

      </main>

      <footer>
        ThermoGrid • Transformer Thermal Intelligence
      </footer>

    </div>
  );
}

export default App;
