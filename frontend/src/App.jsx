import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import NavBar from "./NavBar";
import Login from "./Login";
import Signup from "./Signup";
import TTS from "./TTS";
import STT from "./STT";
import Conversation from "./Conversation";
import HealthcareNavigation from "./HealthcareNavigation";
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
        <Route path="/signup" element={<Signup />} />
        <Route path="/tts" element={<PrivateRoute><TTS /></PrivateRoute>} />
        <Route path="/stt" element={<PrivateRoute><STT /></PrivateRoute>} />
        <Route path="/conversation" element={<PrivateRoute><Conversation /></PrivateRoute>} />
        <Route path="/healthcare" element={<PrivateRoute><HealthcareNavigation /></PrivateRoute>} />
        <Route path="*" element={<Navigate to="/conversation" />} />
      </Routes>
    </Router>
  );
}
