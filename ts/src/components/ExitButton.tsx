import React from "react";

const ExitButton: React.FC = () => {
  const appRoute = "8042"; // Hard-code the app route

  const stopBackendService = async () => {
    try {
      const response = await fetch(`${window.location.protocol}//${window.location.hostname}:8001/systemctl_action/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          app_route: appRoute,
          action: "stop",
        }),
      });

      const result = await response.json();
      console.log("Service stop response:", result);
    } catch (error) {
      console.error("Error stopping service:", error);
    }
  };

  const handleExitClick = async () => {
    await stopBackendService();
    window.location.href = `${window.location.protocol}//${window.location.hostname}/apps/launcher`;
  };

  return (
    <button
      style={{
        position: "absolute",
        bottom: 5,
        left: 10,
        zIndex: 1000,
      }}
      onClick={handleExitClick}
    >
      EXIT
    </button>
  );
};

export default ExitButton;
