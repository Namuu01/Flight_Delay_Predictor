import React, { useEffect, useState } from "react";

import Navbar from "./components/Navbar";
import Home from "./pages/Home";
import Prediction from "./pages/Prediction";

function App() {
  const path = window.location.pathname;

  const [darkMode, setDarkMode] = useState(() => {
    return localStorage.getItem("flightTheme") === "dark";
  });

  useEffect(() => {
    document.body.classList.toggle("dark-mode", darkMode);

    localStorage.setItem(
      "flightTheme",
      darkMode ? "dark" : "light"
    );
  }, [darkMode]);

  function toggleTheme() {
    setDarkMode((previous) => !previous);
  }

  return (
    <>
      <Navbar
        darkMode={darkMode}
        onThemeToggle={toggleTheme}
      />

      {path === "/predict" ? (
        <Prediction />
      ) : (
        <Home />
      )}
    </>
  );
}

export default App;