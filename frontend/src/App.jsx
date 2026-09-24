
import { useEffect, useState } from "react";
import {
  TrainFront,
  Radio,
  Brain,
  AlertTriangle,
  Activity,
  Route,
  CalendarClock,
  ShieldCheck,
  Play,
  Settings,
} from "lucide-react";

import api from "./services/api";
import "./App.css";

function App() {
  const [activeSection, setActiveSection] = useState("dashboard");

  const [dashboardData, setDashboardData] = useState(null);
  const [railwayData, setRailwayData] = useState(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [actionMessage, setActionMessage] = useState("");
  const [movingTrain, setMovingTrain] = useState("");

  const [signalUpdating, setSignalUpdating] = useState("");
  const [platformUpdating, setPlatformUpdating] = useState("");

  // --------------------------------------------------
  // LIVE AI INTELLIGENCE
  // --------------------------------------------------

  const [liveAI, setLiveAI] = useState({
    delay: {},
    signal: {},
    conflict: {},
    anomaly: {},
    congestion: null,
  });

  const [aiLoading, setAiLoading] = useState(false);

  // --------------------------------------------------
  // LOAD DATA
  // --------------------------------------------------

  const loadData = async () => {
    try {
      const [dashboardResponse, railwayResponse] =
        await Promise.all([
          api.get("/dashboard"),
          api.get("/dashboard-live"),
        ]);

      setDashboardData(dashboardResponse.data);
      setRailwayData(railwayResponse.data);

      setError("");
    } catch (err) {
      console.error(err);

      setError(
        "Unable to connect to the Railway AI backend."
      );
    } finally {
      setLoading(false);
    }
  };

  // --------------------------------------------------
  // LIVE AI INTELLIGENCE
  // --------------------------------------------------

  const loadLiveAI = async () => {
    if (!railwayData?.trains?.length) return;

    try {
      setAiLoading(true);

      const trainResults = await Promise.all(
        railwayData.trains.map(async (train) => {
          const id = train.train_id;

          const results = await Promise.allSettled([
            api.get(`/ai-delay-live/${id}`),
            api.get(`/ai-signal-live/${id}`),
            api.get(`/ai-conflict-live/${id}`),
            api.get(`/ai-anomaly-live/${id}`),
          ]);

          return {
            id,
            delay: results[0].status === "fulfilled"
              ? results[0].value.data : null,
            signal: results[1].status === "fulfilled"
              ? results[1].value.data : null,
            conflict: results[2].status === "fulfilled"
              ? results[2].value.data : null,
            anomaly: results[3].status === "fulfilled"
              ? results[3].value.data : null,
          };
        })
      );

      const congestionResponse =
        await api.get("/ai-congestion-live");

      const delay = {};
      const signal = {};
      const conflict = {};
      const anomaly = {};

      trainResults.forEach((item) => {
        delay[item.id] = item.delay;
        signal[item.id] = item.signal;
        conflict[item.id] = item.conflict;
        anomaly[item.id] = item.anomaly;
      });

      setLiveAI({
        delay,
        signal,
        conflict,
        anomaly,
        congestion: congestionResponse.data,
      });
    } catch (err) {
      console.error("Live AI loading failed:", err);
    } finally {
      setAiLoading(false);
    }
  };

  // --------------------------------------------------
  // AUTOMATIC SIMULATION
  // --------------------------------------------------

  useEffect(() => {
    loadData();

    const interval = setInterval(async () => {
      try {
        await api.post("/simulation/tick");
        await loadData();
      } catch (err) {
        console.error("Simulation tick failed:", err);
      }
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (railwayData?.trains?.length) {
      loadLiveAI();
    }
  }, [railwayData]);

  // --------------------------------------------------
  // MOVE TRAIN
  // --------------------------------------------------

  const moveTrain = async (trainId) => {
    try {
      setMovingTrain(trainId);
      setActionMessage("");

      const response = await api.post(
        "/train/move",
        {
          train_id: trainId,
        }
      );

      const result = response.data;

      setActionMessage(
        result.success
          ? `✓ ${result.message}`
          : `⚠ ${result.message}`
      );

      await loadData();
    } catch (err) {
      console.error(err);

      setActionMessage(
        "Unable to move the train."
      );
    } finally {
      setMovingTrain("");
    }
  };

  // --------------------------------------------------
  // MANUAL SIGNAL OVERRIDE
  // --------------------------------------------------

  const changeSignal = async (
    signalId,
    status
  ) => {
    try {
      setSignalUpdating(signalId);
      setActionMessage("");

      const response = await api.post(
        "/manual/signal",
        {
          signal_id: signalId,
          status: status,
        }
      );

      const result = response.data;

      setActionMessage(
        result.success
          ? `✓ ${signalId} changed to ${status}.`
          : `⚠ ${result.message}`
      );

      await loadData();
    } catch (err) {
      console.error(err);

      setActionMessage(
        `Unable to change ${signalId}.`
      );
    } finally {
      setSignalUpdating("");
    }
  };

  // --------------------------------------------------
  // MANUAL PLATFORM OVERRIDE
  // --------------------------------------------------

  const changePlatform = async (
    trainId,
    platformId
  ) => {
    try {
      setPlatformUpdating(trainId);
      setActionMessage("");

      const response = await api.post(
        "/manual/platform",
        {
          train_id: trainId,
          platform_id: platformId,
        }
      );

      const result = response.data;

      setActionMessage(
        result.success
          ? `✓ ${trainId} assigned to ${platformId}.`
          : `⚠ ${result.message}`
      );

      await loadData();
    } catch (err) {
      console.error(err);

      setActionMessage(
        `Unable to move ${trainId} to ${platformId}.`
      );
    } finally {
      setPlatformUpdating("");
    }
  };

  // --------------------------------------------------
  // SIMULATION START
  // --------------------------------------------------

  const startSimulation = async () => {
    try {
      const response = await api.post(
        "/simulation/start"
      );

      setActionMessage(
        response.data.message
      );

      await loadData();
    } catch (err) {
      console.error(err);

      setActionMessage(
        "Unable to start simulation."
      );
    }
  };

  // --------------------------------------------------
  // SIMULATION STOP
  // --------------------------------------------------

  const stopSimulation = async () => {
    try {
      const response = await api.post(
        "/simulation/stop"
      );

      setActionMessage(
        response.data.message
      );

      await loadData();
    } catch (err) {
      console.error(err);

      setActionMessage(
        "Unable to stop simulation."
      );
    }
  };

  const trains =
    railwayData?.trains || [];

  const signals =
    railwayData?.signals_state || [];

  const platforms =
    railwayData?.platforms || [];

  // --------------------------------------------------
  // LIVE AI SUMMARY
  // --------------------------------------------------

  const congestionSections =
    liveAI.congestion?.sections || [];

  const highestCongestionSection =
    liveAI.congestion?.highest_congestion_section || "—";

  const highestCongestionResult =
    liveAI.congestion?.highest_congestion_result || {};

  const congestionLevel =
    highestCongestionResult?.congestion_level ||
    highestCongestionResult?.predicted_level ||
    "UNKNOWN";

  const anomalyTrains = trains.filter((train) => {
    const result = liveAI.anomaly?.[train.train_id];
    const ai = result?.ai_result || result?.prediction || result || {};

    return (
      ai?.is_anomaly === true ||
      ai?.anomaly === true ||
      String(ai?.status || "").toUpperCase() === "ANOMALY"
    );
  });

  const conflictTrains = trains.filter((train) => {
    const result = liveAI.conflict?.[train.train_id];
    const ai = result?.ai_result || result?.prediction || result || {};

    return (
      ai?.conflict === true ||
      ai?.conflict_detected === true ||
      String(ai?.status || "").toUpperCase() === "CONFLICT"
    );
  });

  const delayPredictions = trains
    .map((train) => {
      const result = liveAI.delay?.[train.train_id];
      const ai = result?.ai_prediction || result?.prediction || result || {};
      const predicted =
        ai?.predicted_delay ??
        ai?.delay_prediction ??
        ai?.prediction ??
        null;

      return {
        train,
        predicted:
          typeof predicted === "number" ? predicted : null,
      };
    })
    .filter((item) => item.predicted !== null);

  const highestPredictedDelay =
    delayPredictions.length > 0
      ? delayPredictions.reduce((max, item) =>
          item.predicted > max.predicted ? item : max
        )
      : null;

  const signalRecommendations = trains
    .map((train) => {
      const result = liveAI.signal?.[train.train_id];
      const ai =
        result?.ai_result ||
        result?.ai_recommendation ||
        result ||
        {};

      return {
        train,
        recommendation:
          ai?.recommended_signal ||
          result?.recommended_signal ||
          "—",
      };
    })
    .filter((item) => item.recommendation !== "—");

  const highCongestionSections = congestionSections.filter((section) => {
    const ai = section?.ai_result || {};
    const level = String(
      ai?.congestion_level ||
      ai?.predicted_level ||
      ""
    ).toUpperCase();

    return level === "HIGH";
  });

  return (
    <div className="app">

      {/* ==================================================
          HEADER
      ================================================== */}

      <header className="topbar">

        <div className="brand">

          <TrainFront size={32} />

          <div>

            <h1>
              Railway AI Control Center
            </h1>

            <span>
              AI-Powered Indian Railways Traffic
              Management System
            </span>

          </div>

        </div>

        <div className="system-status">

          <span className="status-dot"></span>

          SYSTEM ONLINE

        </div>

      </header>


      {/* ==================================================
          NAVIGATION
      ================================================== */}

      <nav className="navigation">

        <button
          className={
            activeSection === "dashboard"
              ? "active"
              : ""
          }
          onClick={() =>
            setActiveSection("dashboard")
          }
        >
          Dashboard
        </button>

        <button
          className={
            activeSection === "trains"
              ? "active"
              : ""
          }
          onClick={() =>
            setActiveSection("trains")
          }
        >
          Trains
        </button>

        <button
          className={
            activeSection === "signals"
              ? "active"
              : ""
          }
          onClick={() =>
            setActiveSection("signals")
          }
        >
          Signals
        </button>

        <button
          className={
            activeSection === "ai"
              ? "active"
              : ""
          }
          onClick={() =>
            setActiveSection("ai")
          }
        >
          AI Intelligence
        </button>

        <button
          className={
            activeSection === "override"
              ? "active"
              : ""
          }
          onClick={() =>
            setActiveSection("override")
          }
        >
          Manual Override
        </button>

      </nav>


      {/* ==================================================
          MAIN
      ================================================== */}

      <main className="main-content">

        {error && (
          <div
            style={{
              background: "#451a1a",
              border: "1px solid #7f1d1d",
              color: "#fca5a5",
              padding: "12px 16px",
              borderRadius: "8px",
              marginBottom: "20px",
            }}
          >
            {error}
          </div>
        )}


        {actionMessage && (
          <div
            style={{
              background:
                actionMessage.startsWith("✓")
                  ? "#052e16"
                  : "#451a1a",

              border:
                actionMessage.startsWith("✓")
                  ? "1px solid #166534"
                  : "1px solid #7f1d1d",

              color:
                actionMessage.startsWith("✓")
                  ? "#86efac"
                  : "#fca5a5",

              padding: "12px 16px",
              borderRadius: "8px",
              marginBottom: "20px",
            }}
          >
            {actionMessage}
          </div>
        )}


        {/* ==================================================
            PAGE HEADER
        ================================================== */}

        <div className="page-heading">

          <div>

            <h2>
              AI Railway Traffic Dashboard
            </h2>

            <p>
              Real-time railway traffic monitoring
              and AI decision support
            </p>

          </div>

          <div className="live-indicator">

            <span></span>

            LIVE

          </div>

        </div>


        {/* ==================================================
            SIMULATION CONTROLS
        ================================================== */}

        <div
          style={{
            display: "flex",
            gap: "10px",
            marginBottom: "20px",
          }}
        >

          <button
            onClick={startSimulation}
            style={{
              background: "#166534",
              color: "white",
              border: "none",
              borderRadius: "6px",
              padding: "10px 18px",
              fontWeight: "600",
              cursor: "pointer",
            }}
          >
            ▶ START SIMULATION
          </button>

          <button
            onClick={stopSimulation}
            style={{
              background: "#991b1b",
              color: "white",
              border: "none",
              borderRadius: "6px",
              padding: "10px 18px",
              fontWeight: "600",
              cursor: "pointer",
            }}
          >
            ⏸ STOP SIMULATION
          </button>

        </div>


        {/* ==================================================
            STATS
        ================================================== */}

        <section className="stats-grid">

          <div className="stat-card">

            <div className="stat-icon">
              <TrainFront />
            </div>

            <div>
              <span>
                Active Trains
              </span>

              <strong>
                {loading
                  ? "..."
                  : railwayData?.active_trains ??
                    0}
              </strong>
            </div>

          </div>


          <div className="stat-card">

            <div className="stat-icon">
              <Radio />
            </div>

            <div>
              <span>
                Active Signals
              </span>

              <strong>
                {loading
                  ? "..."
                  : railwayData?.signals ??
                    0}
              </strong>
            </div>

          </div>


          <div className="stat-card">

            <div className="stat-icon">
              <AlertTriangle />
            </div>

            <div>
              <span>
                Occupied Platforms
              </span>

              <strong>
                {loading
                  ? "..."
                  : railwayData?.occupied_platforms ??
                    0}
              </strong>
            </div>

          </div>


          <div className="stat-card">

            <div className="stat-icon">
              <Activity />
            </div>

            <div>
              <span>
                Network Status
              </span>

              <strong>
                {dashboardData?.network_status ||
                  "UNKNOWN"}
              </strong>
            </div>

          </div>

        </section>


        {/* ==================================================
            DASHBOARD
        ================================================== */}

        <section className="dashboard-grid">

          <div className="panel railway-panel">

            <div className="panel-header">

              <div>

                <h3>
                  Live Railway Network
                </h3>

                <p>
                  Connected to Railway Simulation
                  State
                </p>

              </div>

              <span className="panel-status">
                LIVE
              </span>

            </div>


            <div className="railway-map">

              <div className="direction left">
                ORIGIN
              </div>

              <div className="direction right">
                DESTINATION
              </div>


              {trains
                .slice(0, 4)
                .map((train, index) => (

                  <div
                    className={`track track-${index + 1}`}
                    key={train.train_id}
                  >

                    <div
                      className={`signal ${
                        train.signal === "RED"
                          ? "red"
                          : train.signal ===
                            "YELLOW"
                          ? "yellow"
                          : "green"
                      }`}
                    ></div>


                    <div
                      className="train"
                      style={{
                        marginLeft:
                          `${Math.min(
                            Math.max(
                              train.position,
                              5
                            ),
                            90
                          )}%`,
                      }}
                    >
                      🚆 {train.train_id}
                    </div>


                    <div
                      className={`signal ${
                        train.signal === "RED"
                          ? "red"
                          : train.signal ===
                            "YELLOW"
                          ? "yellow"
                          : "green"
                      }`}
                    ></div>

                  </div>

                ))}


              {platforms.map(
                (platform, index) => (

                  <div
                    className="platform"
                    key={
                      platform.platform_id
                    }
                    style={{
                      top:
                        `${110 + index * 70}px`,
                    }}
                  >

                    {platform.platform_id}

                    {platform.occupied
                      ? ` • ${platform.train_id}`
                      : " • FREE"}

                  </div>

                )
              )}

            </div>

          </div>


          {/* AI */}

          <div className="panel">

            <div className="panel-header">

              <div>

                <h3>
                  AI Intelligence
                </h3>

                <p>
                  Current AI module status
                </p>

              </div>

              <Brain />

            </div>


            <div className="ai-list">

              <AIStatus
                icon={<Activity />}
                name="Delay Prediction AI"
                status={
                  dashboardData?.ai?.delay
                }
              />

              <AIStatus
                icon={<Radio />}
                name="Signal Control AI"
                status={
                  dashboardData?.ai?.signal
                }
              />

              <AIStatus
                icon={<AlertTriangle />}
                name="Conflict AI"
                status={
                  dashboardData?.ai?.conflict
                }
              />

              <AIStatus
                icon={<Activity />}
                name="Anomaly Detection AI"
                status={
                  dashboardData?.ai?.anomaly
                }
              />

              <AIStatus
                icon={<Activity />}
                name="Congestion GNN"
                status={
                  dashboardData?.ai?.congestion
                }
              />

              <AIStatus
                icon={<Route />}
                name="Reroute AI"
                status={
                  dashboardData?.ai?.reroute
                }
              />

              <AIStatus
                icon={<CalendarClock />}
                name="Timetable AI"
                status={
                  dashboardData?.ai?.timetable ||
                  "ACTIVE"
                }
              />

              <AIStatus
                icon={<ShieldCheck />}
                name="Incident Response AI"
                status={
                  dashboardData?.ai?.incident
                }
              />

            </div>

          </div>

        </section>


        {/* ==================================================
            TRAIN CONTROL
        ================================================== */}

        <section
          className="panel"
          style={{
            marginTop: "20px",
          }}
        >

          <div className="panel-header">

            <div>

              <h3>
                Live Train Control
              </h3>

              <p>
                Operator-controlled train
                movement
              </p>

            </div>

            <TrainFront />

          </div>


          <div
            style={{
              overflowX: "auto",
            }}
          >

            <table
              style={{
                width: "100%",
                borderCollapse:
                  "collapse",
              }}
            >

              <thead>

                <tr>

                  <th>Train</th>
                  <th>Position</th>
                  <th>Speed</th>
                  <th>Signal</th>
                  <th>Controlling Signal</th>
                  <th>Platform</th>
                  <th>Status</th>
                  <th>Delay</th>
                  <th>Control</th>

                </tr>

              </thead>


              <tbody>

                {trains.map((train) => {

                  const canMove =
                    train.signal === "YELLOW" ||
                    train.signal ===
                      "DOUBLE YELLOW" ||
                    train.signal === "GREEN";

                  return (

                    <tr
                      key={train.train_id}
                      style={{
                        borderTop:
                          "1px solid #263244",
                      }}
                    >

                      <td>
                        🚆 {train.train_id}
                      </td>

                      <td>
                        {Number(
                          train.position
                        ).toFixed(1)}
                      </td>

                      <td>
                        {train.speed}
                      </td>

                      <td
                        style={{
                          color:
                            train.signal ===
                            "RED"
                              ? "#f87171"
                              : train.signal ===
                                "GREEN"
                              ? "#4ade80"
                              : "#facc15",
                          fontWeight: "600",
                        }}
                      >
                        {train.signal}
                      </td>

                      <td>
                        {train.controlling_signal}
                      </td>

                      <td>
                        {train.platform ||
                          "—"}
                      </td>

                      <td>
                        {train.status}
                      </td>

                      <td>
                        {train.delay} min
                      </td>

                      <td>

                        <button
                          onClick={() =>
                            moveTrain(
                              train.train_id
                            )
                          }
                          disabled={
                            movingTrain ===
                            train.train_id
                          }
                          style={{
                            background:
                              canMove
                                ? "#166534"
                                : "#7f1d1d",
                            color: "white",
                            border: "none",
                            borderRadius:
                              "6px",
                            padding:
                              "7px 12px",
                            cursor:
                              "pointer",
                          }}
                        >
                          <Play
                            size={13}
                            style={{
                              marginRight:
                                "4px",
                              verticalAlign:
                                "middle",
                            }}
                          />

                          {movingTrain ===
                          train.train_id
                            ? "MOVING..."
                            : "MOVE"}
                        </button>

                      </td>

                    </tr>

                  );
                })}

              </tbody>

            </table>

          </div>

        </section>


        {/* ==================================================
            MANUAL OVERRIDE
        ================================================== */}

        {activeSection === "override" && (

          <section
            className="panel"
            style={{
              marginTop: "20px",
            }}
          >

            <div className="panel-header">

              <div>

                <h3>
                  Manual Override Control Center
                </h3>

                <p>
                  Direct operator control of
                  railway signals and platforms
                </p>

              </div>

              <Settings />

            </div>


            {/* WARNING */}

            <div
              style={{
                background: "#422006",
                border:
                  "1px solid #92400e",
                color: "#fde68a",
                padding: "14px",
                borderRadius: "8px",
                marginBottom: "20px",
              }}
            >

              <strong>
                MANUAL OPERATOR CONTROL
              </strong>

              <p
                style={{
                  marginBottom: 0,
                }}
              >
                Changes made here directly modify
                the railway simulation state.
                Manual signal changes override
                the current automatic signal mode.
              </p>

            </div>


            {/* ==================================================
                SIGNAL OVERRIDE
            ================================================== */}

            <h3>
              🚦 Signal Override
            </h3>

            <div
              style={{
                display: "grid",
                gridTemplateColumns:
                  "repeat(auto-fit, minmax(280px, 1fr))",
                gap: "15px",
                marginTop: "15px",
              }}
            >

              {signals.map((signal) => {

                const controlledTrain =
                  trains.find(
                    (train) =>
                      train.controlling_signal ===
                      signal.signal_id
                  );

                return (

                  <div
                    key={signal.signal_id}
                    style={{
                      border:
                        "1px solid #263244",
                      borderRadius: "10px",
                      padding: "15px",
                      background:
                        "#111827",
                    }}
                  >

                    <div
                      style={{
                        display: "flex",
                        justifyContent:
                          "space-between",
                        alignItems:
                          "center",
                        marginBottom:
                          "10px",
                      }}
                    >

                      <strong>
                        {signal.signal_id}
                      </strong>

                      <span
                        style={{
                          color:
                            signal.status ===
                            "RED"
                              ? "#f87171"
                              : signal.status ===
                                "GREEN"
                              ? "#4ade80"
                              : "#facc15",
                          fontWeight:
                            "700",
                        }}
                      >
                        {signal.status}
                      </span>

                    </div>


                    <div
                      style={{
                        fontSize:
                          "12px",
                        color:
                          "#94a3b8",
                        marginBottom:
                          "12px",
                      }}
                    >

                      Mode: {signal.mode}

                      <br />

                      {controlledTrain
                        ? `Controls ${controlledTrain.train_id}`
                        : "No assigned train"}

                    </div>


                    <div
                      style={{
                        display: "grid",
                        gridTemplateColumns:
                          "1fr 1fr",
                        gap: "7px",
                      }}
                    >

                      {[
                        "RED",
                        "DOUBLE YELLOW",
                        "YELLOW",
                        "GREEN",
                      ].map((status) => (

                        <button
                          key={status}
                          onClick={() =>
                            changeSignal(
                              signal.signal_id,
                              status
                            )
                          }
                          disabled={
                            signalUpdating ===
                            signal.signal_id
                          }
                          style={{
                            padding:
                              "8px 5px",
                            border:
                              "1px solid #374151",
                            borderRadius:
                              "6px",
                            cursor:
                              "pointer",
                            background:
                              signal.status ===
                              status
                                ? "#374151"
                                : "#1f2937",
                            color:
                              status ===
                              "RED"
                                ? "#f87171"
                                : status ===
                                  "GREEN"
                                ? "#4ade80"
                                : "#facc15",
                            fontSize:
                              "11px",
                            fontWeight:
                              "600",
                          }}
                        >
                          {status}
                        </button>

                      ))}

                    </div>

                  </div>

                );
              })}

            </div>


            {/* ==================================================
                PLATFORM OVERRIDE
            ================================================== */}

            <h3
              style={{
                marginTop: "30px",
              }}
            >
              🚆 Platform Override
            </h3>

            <div
              style={{
                display: "grid",
                gridTemplateColumns:
                  "repeat(auto-fit, minmax(280px, 1fr))",
                gap: "15px",
                marginTop: "15px",
              }}
            >

              {trains.map((train) => (

                <div
                  key={train.train_id}
                  style={{
                    border:
                      "1px solid #263244",
                    borderRadius: "10px",
                    padding: "15px",
                    background:
                      "#111827",
                  }}
                >

                  <strong>
                    🚆 {train.train_id}
                  </strong>

                  <div
                    style={{
                      color:
                        "#94a3b8",
                      fontSize:
                        "12px",
                      margin:
                        "8px 0 12px",
                    }}
                  >
                    Current Platform:{" "}
                    <strong>
                      {train.platform ||
                        "NONE"}
                    </strong>
                  </div>


                  <div
                    style={{
                      display: "grid",
                      gridTemplateColumns:
                        "repeat(2, 1fr)",
                      gap: "7px",
                    }}
                  >

                    {platforms.map(
                      (platform) => (

                        <button
                          key={
                            platform.platform_id
                          }
                          onClick={() =>
                            changePlatform(
                              train.train_id,
                              platform.platform_id
                            )
                          }
                          disabled={
                            platformUpdating ===
                            train.train_id
                          }
                          style={{
                            padding:
                              "8px",
                            border:
                              "1px solid #374151",
                            borderRadius:
                              "6px",
                            background:
                              train.platform ===
                              platform.platform_id
                                ? "#374151"
                                : "#1f2937",
                            color:
                              "white",
                            cursor:
                              "pointer",
                            fontWeight:
                              "600",
                          }}
                        >
                          {platform.platform_id}
                        </button>

                      )
                    )}

                  </div>

                </div>

              ))}

            </div>

          </section>

        )}


        {/* ==================================================
            AI SITUATION
        ================================================== */}

        <section className="bottom-grid">

          <div className="panel">

            <div className="panel-header">

              <div>

                <h3>
                  AI Situation Analysis
                </h3>

                <p>
                  Current railway network
                  conditions
                </p>

              </div>

              <Brain />

            </div>


            <div className="analysis-content">

              <div className="analysis-item">
                <span>CONGESTION</span>
                <strong
                  className={
                    congestionLevel === "HIGH"
                      ? "danger"
                      : congestionLevel === "MEDIUM"
                      ? "warning"
                      : "safe"
                  }
                >
                  {aiLoading ? "ANALYZING..." : congestionLevel}
                </strong>
              </div>

              <div className="analysis-item">
                <span>WORST SECTION</span>
                <strong className="warning">
                  {highestCongestionSection}
                </strong>
              </div>

              <div className="analysis-item">
                <span>ANOMALIES</span>
                <strong className={anomalyTrains.length ? "danger" : "safe"}>
                  {anomalyTrains.length
                    ? `${anomalyTrains.length} DETECTED`
                    : "NONE DETECTED"}
                </strong>
              </div>

              <div className="analysis-item">
                <span>TRAIN CONFLICT</span>
                <strong className={conflictTrains.length ? "danger" : "safe"}>
                  {conflictTrains.length
                    ? `${conflictTrains.length} DETECTED`
                    : "NONE DETECTED"}
                </strong>
              </div>

              <div className="analysis-item">
                <span>PREDICTED DELAY</span>
                <strong className="warning">
                  {highestPredictedDelay
                    ? `${highestPredictedDelay.train.train_id}: ${Number(
                        highestPredictedDelay.predicted
                      ).toFixed(1)} min`
                    : "NO DATA"}
                </strong>
              </div>

              <div className="analysis-item">
                <span>SIGNAL AI</span>
                <strong className="safe">
                  {signalRecommendations.length
                    ? `${signalRecommendations.length} RECOMMENDATIONS`
                    : "MONITORING"}
                </strong>
              </div>

              <div className="analysis-item">
                <span>HIGH CONGESTION SECTIONS</span>
                <strong className={highCongestionSections.length ? "danger" : "safe"}>
                  {highCongestionSections.length}
                </strong>
              </div>

              <div className="analysis-item">
                <span>REROUTING</span>
                <strong className="safe">
                  INCIDENT-DRIVEN AI
                </strong>
              </div>

            </div>

          </div>


          <div className="panel">

            <div className="panel-header">
              <div>
                <h3>Live AI Operations</h3>
                <p>AI predictions from the current simulator state</p>
              </div>
              <Brain />
            </div>

            <div style={{ display: "grid", gap: "10px" }}>

              <div style={{
                padding: "12px",
                border: "1px solid #263244",
                borderRadius: "8px",
                background: "#111827"
              }}>
                <strong>Congestion GNN</strong>
                <div style={{ marginTop: "6px", color: "#94a3b8", fontSize: "13px" }}>
                  Sections analyzed: {congestionSections.length}
                  <br />
                  Highest section: {highestCongestionSection}
                  <br />
                  Current level: {congestionLevel}
                </div>
              </div>

              <div style={{
                padding: "12px",
                border: "1px solid #263244",
                borderRadius: "8px",
                background: "#111827"
              }}>
                <strong>Anomaly Detection</strong>
                <div style={{
                  marginTop: "6px",
                  color: anomalyTrains.length ? "#fca5a5" : "#86efac",
                  fontSize: "13px"
                }}>
                  {anomalyTrains.length
                    ? anomalyTrains.map((t) => t.train_id).join(", ")
                    : "No live anomalies detected"}
                </div>
              </div>

              <div style={{
                padding: "12px",
                border: "1px solid #263244",
                borderRadius: "8px",
                background: "#111827"
              }}>
                <strong>Conflict Detection</strong>
                <div style={{
                  marginTop: "6px",
                  color: conflictTrains.length ? "#fca5a5" : "#86efac",
                  fontSize: "13px"
                }}>
                  {conflictTrains.length
                    ? conflictTrains.map((t) => t.train_id).join(", ")
                    : "No live conflicts detected"}
                </div>
              </div>

              <div style={{
                padding: "12px",
                border: "1px solid #263244",
                borderRadius: "8px",
                background: "#111827"
              }}>
                <strong>Delay Prediction</strong>
                <div style={{
                  marginTop: "6px",
                  color: "#facc15",
                  fontSize: "13px"
                }}>
                  {highestPredictedDelay
                    ? `${highestPredictedDelay.train.train_id} — predicted delay ${Number(
                        highestPredictedDelay.predicted
                      ).toFixed(1)} min`
                    : "No live delay prediction available"}
                </div>
              </div>

              <div style={{
                padding: "12px",
                border: "1px solid #263244",
                borderRadius: "8px",
                background: "#111827"
              }}>
                <strong>Signal AI</strong>
                <div style={{
                  marginTop: "6px",
                  color: "#93c5fd",
                  fontSize: "13px"
                }}>
                  {signalRecommendations.length
                    ? signalRecommendations
                        .slice(0, 4)
                        .map((item) =>
                          `${item.train.train_id}: ${item.recommendation}`
                        )
                        .join(" • ")
                    : "No signal recommendations available"}
                </div>
              </div>

              <div style={{
                padding: "12px",
                border: "1px solid #263244",
                borderRadius: "8px",
                background: "#111827"
              }}>
                <strong>Reroute AI</strong>
                <div style={{
                  marginTop: "6px",
                  color: "#86efac",
                  fontSize: "13px"
                }}>
                  Incident-driven monitoring active.
                  Congestion alone does not trigger rerouting.
                </div>
              </div>

            </div>
          </div>


          <div className="panel">

            <div className="panel-header">

              <div>

                <h3>
                  Railway State
                </h3>

                <p>
                  Current simulator state
                </p>

              </div>

              <ShieldCheck />

            </div>


            <div className="recommendations">

              <div>
                <span>
                  TRAINS
                </span>
                {trains.length}
              </div>

              <div>
                <span>
                  SIGNALS
                </span>
                {signals.length}
              </div>

              <div>
                <span>
                  PLATFORMS
                </span>
                {platforms.length}
              </div>

              <div>
                <span>
                  SIMULATION
                </span>

                {railwayData?.simulation_running
                  ? "RUNNING"
                  : "STOPPED"}
              </div>

            </div>

          </div>

        </section>


        {/* ==================================================
            OPERATOR NOTICE
        ================================================== */}

        <div className="operator-notice">

          <ShieldCheck size={22} />

          <div>

            <strong>
              Operator Control
            </strong>

            <p>
              AI provides decision support.
              Final operational control remains
              with the authorized operator.
            </p>

          </div>

        </div>

      </main>

    </div>
  );
}


// ======================================================
// AI STATUS COMPONENT
// ======================================================

function AIStatus({
  icon,
  name,
  status,
}) {

  const active =
    status === "ACTIVE";

  return (

    <div className="ai-status">

      <div className="ai-name">

        {icon}

        <span>
          {name}
        </span>

      </div>

      <div
        className="ai-active"
        style={{
          color: active
            ? "#86efac"
            : "#f87171",
        }}
      >

        <span
          style={{
            background:
              active
                ? "#22c55e"
                : "#ef4444",
          }}
        ></span>

        {status || "UNKNOWN"}

      </div>

    </div>

  );
}


export default App;
