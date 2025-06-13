import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import CssBaseline from "@mui/material/CssBaseline";
import "@fontsource/inter/400.css";
import "@fontsource/inter/700.css";
import { createTheme, ThemeProvider } from "@mui/material/styles";

const theme = createTheme({
  typography: {
    fontFamily: 'Inter, Arial, sans-serif',
  },
  palette: {
    primary: { main: "#5f6fff" },
    secondary: { main: "#00e6d8" },
    background: { default: "#f7fafd" },
  },
});

const bgStyle = {
  minHeight: "100vh",
  minWidth: "100vw",
  background: "linear-gradient(120deg, #5f6fff 0%, #00e6d8 100%)",
  backgroundAttachment: "fixed",
  position: "fixed",
  top: 0,
  left: 0,
  zIndex: -1,
  width: "100vw",
  height: "100vh",
  filter: "blur(0px)",
  opacity: 0.9,
};

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <div style={bgStyle} />
      <App />
    </ThemeProvider>
  </React.StrictMode>
);
