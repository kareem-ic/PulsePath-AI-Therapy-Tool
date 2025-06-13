import { AppBar, Toolbar, Typography, Button, Box } from "@mui/material";
import { Link, useNavigate } from "react-router-dom";
import { clearToken, getToken } from "./api";
import { motion } from "framer-motion";

export default function NavBar() {
  const navigate = useNavigate();
  const loggedIn = !!getToken();

  const handleLogout = () => {
    clearToken();
    navigate("/login");
  };

  return (
    <AppBar
      position="static"
      elevation={0}
      sx={{
        background: "rgba(255,255,255,0.15)",
        boxShadow: "0 8px 32px 0 rgba(31, 38, 135, 0.15)",
        backdropFilter: "blur(12px)",
        borderBottom: "1.5px solid rgba(255,255,255,0.18)",
      }}
    >
      <Toolbar>
        <Typography
          variant="h6"
          sx={{
            flexGrow: 1,
            fontWeight: 700,
            letterSpacing: 1,
            color: "#222",
            textShadow: "0 1px 8px rgba(95,111,255,0.08)"
          }}
        >
          PulsePath AI Therapy
        </Typography>
        <Box sx={{ display: "flex", gap: 1 }}>
          <motion.div whileHover={{ scale: 1.08 }} whileTap={{ scale: 0.97 }}>
            <Button color="inherit" component={Link} to="/tts" sx={{ fontWeight: 600, borderRadius: 3 }}>
              TTS
            </Button>
          </motion.div>
          <motion.div whileHover={{ scale: 1.08 }} whileTap={{ scale: 0.97 }}>
            <Button color="inherit" component={Link} to="/stt" sx={{ fontWeight: 600, borderRadius: 3 }}>
              STT
            </Button>
          </motion.div>
          <motion.div whileHover={{ scale: 1.08 }} whileTap={{ scale: 0.97 }}>
            <Button color="inherit" component={Link} to="/conversation" sx={{ fontWeight: 600, borderRadius: 3 }}>
              Conversation
            </Button>
          </motion.div>
          {loggedIn ? (
            <motion.div whileHover={{ scale: 1.08 }} whileTap={{ scale: 0.97 }}>
              <Button color="inherit" onClick={handleLogout} sx={{ fontWeight: 600, borderRadius: 3 }}>
                Logout
              </Button>
            </motion.div>
          ) : (
            <>
              <motion.div whileHover={{ scale: 1.08 }} whileTap={{ scale: 0.97 }}>
                <Button color="inherit" component={Link} to="/login" sx={{ fontWeight: 600, borderRadius: 3 }}>
                  Login
                </Button>
              </motion.div>
              <motion.div whileHover={{ scale: 1.08 }} whileTap={{ scale: 0.97 }}>
                <Button color="inherit" component={Link} to="/signup" sx={{ fontWeight: 600, borderRadius: 3 }}>
                  Sign Up
                </Button>
              </motion.div>
            </>
          )}
        </Box>
      </Toolbar>
    </AppBar>
  );
}
