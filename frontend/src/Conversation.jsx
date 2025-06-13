import { useState, useRef, useEffect } from "react";
import { TextField, Button, Container, Typography, Box, Paper, Chip, Alert, Stack } from "@mui/material";
import { apiRequest } from "./api";
import { motion, AnimatePresence } from "framer-motion";

const bubbleStyles = {
  user: {
    background: "linear-gradient(120deg, #5f6fff 60%, #00e6d8 100%)",
    color: "white",
    alignSelf: "flex-end",
    borderRadius: "18px 18px 6px 18px",
    padding: "14px 20px",
    maxWidth: "75%",
    marginBottom: 8,
    marginLeft: "auto",
    boxShadow: "0 2px 16px 0 rgba(95,111,255,0.10)",
    fontWeight: 500,
    fontSize: 17
  },
  ai: {
    background: "rgba(255,255,255,0.35)",
    color: "#222",
    alignSelf: "flex-start",
    borderRadius: "18px 18px 18px 6px",
    padding: "14px 20px",
    maxWidth: "75%",
    marginBottom: 8,
    marginRight: "auto",
    boxShadow: "0 2px 16px 0 rgba(0,230,216,0.10)",
    fontWeight: 500,
    fontSize: 17,
    backdropFilter: "blur(8px)"
  }
};

const moodColors = {
  happy: "#ffd600",
  sad: "#1976d2",
  angry: "#ff7043",
  anxious: "#ba68c8",
  excited: "#00e676",
  neutral: "#bdbdbd",
  overwhelmed: "#ffb300"
};

function MoodBar({ mood }) {
  if (!mood || mood.length === 0) return null;
  const last = mood[mood.length - 1];
  const color = moodColors[last.sentiment] || "#bdbdbd";
  return (
    <Box mb={2} display="flex" alignItems="center" gap={1}>
      <Typography variant="subtitle2">Mood trend:</Typography>
      <Box width={48} height={20} borderRadius={2} bgcolor={color} title={`${last.sentiment} (${Math.round(last.confidence * 100)}%)`} />
      <Typography variant="body2">{last.sentiment} ({Math.round(last.confidence * 100)}%)</Typography>
    </Box>
  );
}

export default function Conversation() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [mood, setMood] = useState([]);
  const listRef = useRef(null);

  useEffect(() => {
    apiRequest("/chat-history").then(res => {
      if (res.history) setMessages(res.history);
    });
    apiRequest("/mood-history").then(res => {
      if (res.mood) setMood(res.mood);
    });
  }, []);

  useEffect(() => {
    if (listRef.current) {
      listRef.current.scrollTop = listRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");
    if (!input.trim()) return;
    const userMsg = { sender: "user", text: input };
    setMessages((msgs) => [...msgs, userMsg]);
    setInput("");
    try {
      const res = await apiRequest("/conversation", "POST", { text: userMsg.text });
      if (res.ai_response) {
        setMessages((msgs) => [
          ...msgs,
          {
            sender: "ai",
            text: res.ai_response,
            label: res.label,
            confidence: res.confidence
          }
        ]);
        apiRequest("/mood-history").then(res => {
          if (res.mood) setMood(res.mood);
        });
      } else {
        setError(res.error || "Error getting AI response");
      }
    } catch {
      setError("Error getting AI response");
    }
  };

  const handleClear = async () => {
    setError("");
    setSuccess("");
    try {
      const res = await apiRequest("/delete-history", "POST");
      if (res.message) {
        setMessages([]);
        setSuccess("Chat history cleared.");
        setMood([]);
      } else {
        setError(res.error || "Error clearing chat history");
      }
    } catch {
      setError("Error clearing chat history");
    }
  };

  return (
    <Container maxWidth="sm">
      <Box mt={8}>
        <Typography variant="h5" align="center" gutterBottom sx={{ fontWeight: 700, letterSpacing: 1, color: "#222" }}>
          Conversation
        </Typography>
        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
        {success && <Alert severity="success" sx={{ mb: 2 }}>{success}</Alert>}
        <MoodBar mood={mood} />
        <Paper
          variant="outlined"
          sx={{
            height: 370,
            overflowY: "auto",
            p: 2,
            mb: 2,
            display: 'flex',
            flexDirection: 'column',
            borderRadius: 5,
            background: "rgba(255,255,255,0.25)",
            boxShadow: "0 8px 32px 0 rgba(31, 38, 135, 0.10)",
            backdropFilter: "blur(12px)"
          }}
          ref={listRef}
        >
          <AnimatePresence initial={false}>
            {messages.map((msg, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 20 }}
                transition={{ duration: 0.32, type: "spring" }}
                style={{ display: "flex" }}
              >
                <Box sx={bubbleStyles[msg.sender]}>
                  <strong>{msg.sender === "user" ? "You" : "AI"}:</strong> {msg.text}
                  {msg.sender === "user" && msg.label && (
                    <Chip
                      label={`Sentiment: ${msg.label} (${(msg.confidence * 100).toFixed(0)}%)`}
                      size="small"
                      color={msg.label === "positive" ? "success" : msg.label === "negative" ? "error" : "default"}
                      sx={{ ml: 1 }}
                    />
                  )}
                  {msg.sender === "ai" && msg.label && (
                    <Chip
                      label={`${msg.label} (${(msg.confidence * 100).toFixed(0)}%)`}
                      size="small"
                      color={msg.label === "positive" ? "success" : msg.label === "negative" ? "error" : "default"}
                      sx={{ ml: 1 }}
                    />
                  )}
                </Box>
              </motion.div>
            ))}
          </AnimatePresence>
        </Paper>
        <Stack direction="row" spacing={2} mb={2}>
          <motion.form
            onSubmit={handleSend}
            style={{ display: "flex", flex: 1, gap: 8 }}
            initial={false}
            animate={{ scale: 1 }}
            whileFocus={{ scale: 1.01 }}
          >
            <TextField
              label="Type your message..."
              value={input}
              onChange={e => setInput(e.target.value)}
              fullWidth
              autoFocus
              sx={{
                background: "rgba(255,255,255,0.7)",
                borderRadius: 3,
                boxShadow: "0 2px 8px 0 rgba(95,111,255,0.08)",
                input: { fontWeight: 500, fontSize: 16 }
              }}
            />
            <motion.div whileHover={{ scale: 1.08 }} whileTap={{ scale: 0.97 }}>
              <Button
                type="submit"
                variant="contained"
                color="primary"
                sx={{
                  borderRadius: 3,
                  fontWeight: 700,
                  px: 3,
                  boxShadow: "0 2px 8px 0 rgba(95,111,255,0.10)",
                  background: "linear-gradient(120deg, #5f6fff 60%, #00e6d8 100%)"
                }}
              >
                Send
              </Button>
            </motion.div>
          </motion.form>
          <motion.div whileHover={{ scale: 1.08 }} whileTap={{ scale: 0.97 }}>
            <Button
              variant="outlined"
              color="secondary"
              onClick={handleClear}
              sx={{
                minWidth: 120,
                borderRadius: 3,
                fontWeight: 700,
                px: 2,
                background: "rgba(255,255,255,0.7)",
                boxShadow: "0 2px 8px 0 rgba(0,230,216,0.08)"
              }}
            >
              Clear Chat
            </Button>
          </motion.div>
        </Stack>
      </Box>
    </Container>
  );
} 