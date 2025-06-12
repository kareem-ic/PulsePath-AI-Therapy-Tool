import { AppBar, Toolbar, Typography, Button } from "@mui/material";
import { Link, useNavigate } from "react-router-dom";
import { clearToken, getToken } from "./api";

export default function NavBar() {
  const navigate = useNavigate();
  const loggedIn = !!getToken();

  const handleLogout = () => {
    clearToken();
    navigate("/login");
  };

  return (
    <AppBar position="static">
      <Toolbar>
        <Typography variant="h6" sx={{ flexGrow: 1 }}>
          PulsePath AI Therapy
        </Typography>
        <Button color="inherit" component={Link} to="/sentiment">Sentiment</Button>
        <Button color="inherit" component={Link} to="/tts">TTS</Button>
        <Button color="inherit" component={Link} to="/stt">STT</Button>
        {loggedIn ? (
          <Button color="inherit" onClick={handleLogout}>Logout</Button>
        ) : (
          <Button color="inherit" component={Link} to="/login">Login</Button>
        )}
      </Toolbar>
    </AppBar>
  );
}
