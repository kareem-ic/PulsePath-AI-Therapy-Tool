import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import NavBar from "./NavBar";
import Login from "./Login";
import Sentiment from "./Sentiment";
import TTS from "./TTS";
import STT from "./STT";
import { getToken } from "./api";

function PrivateRoute({ children }) {
  return getToken() ? children : <Navigate to="/login" />;
}

export default function App() {
  return (
    <Router>
      <NavBar />
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/sentiment" element={<PrivateRoute><Sentiment /></PrivateRoute>} />
        <Route path="/tts" element={<PrivateRoute><TTS /></PrivateRoute>} />
        <Route path="/stt" element={<PrivateRoute><STT /></PrivateRoute>} />
        <Route path="*" element={<Navigate to="/sentiment" />} />
      </Routes>
    </Router>
  );
}
