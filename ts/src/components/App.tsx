import ExitButton from "./ExitButton";

import React, { useEffect, useRef } from "react";

// Define types for style objects
const styles: { [key: string]: React.CSSProperties } = {
  container: {
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    padding: "10px",
    fontFamily: "Arial, sans-serif",
    backgroundSize: "cover",
    backgroundRepeat: "no-repeat",
    backgroundPosition: "center center",
    minHeight: "100vh",
    maxWidth: "1280px",
    margin: "0 auto",
    overflowY: "auto",
  },
  button: {
    padding: "12px 24px",
    fontSize: "50px",
    cursor: "pointer",
    border: "none",
    borderRadius: "6px",
    backgroundColor: "#d9534f",
    color: "#fff",
    userSelect: "none",
  },
};

function App(): JSX.Element {
  const ws = useRef<WebSocket | null>(null);

  useEffect(() => {
    const host = window.location.hostname;
    ws.current = new WebSocket(`ws://${host}:8010/ws`);

    ws.current.onopen = () => {
      console.log("WebSocket connection opened");
    };

    ws.current.onmessage = (event: MessageEvent) => {
      console.log("Received from server:", event.data);
    };

    ws.current.onerror = (error: Event) => {
      console.error("WebSocket error:", error);
    };

    ws.current.onclose = () => {
      console.log("WebSocket connection closed");
    };

    return () => {
      ws.current?.close(); // optional chaining to ensure null safety
    };
  }, []);

  const handleShutdown = (): void => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({ action: "shutdown" }));
      alert("Shutdown command sent");
    } else {
      alert("WebSocket not connected");
    }
  };

  return (
    <div style={styles.container}>
      <button style={styles.button} onClick={handleShutdown}>
        Shutdown
      </button>
       <ExitButton />

    </div>
  );
}

export default App;
