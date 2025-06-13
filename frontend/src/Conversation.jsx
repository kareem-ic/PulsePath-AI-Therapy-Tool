import { useState, useRef, useEffect } from "react";
import { TextField, Button, Container, Typography, Box, Paper, List, ListItem, ListItemText, Chip, Alert, Stack, LinearProgress } from "@mui/material";
import { apiRequest } from "./api";

const bubbleStyles = {
  user: {
    background: "#1976d2",
    color: "white",
    alignSelf: "flex-end",
    borderRadius: "16px 16px 4px 16px",
    padding: "10px 16px",
    maxWidth: "75%",
    marginBottom: 4,
    marginLeft: "auto"
  },
  ai: {
    background: "#f1f1f1",
    color: "#222",
    alignSelf: "flex-start",
    borderRadius: "16px 16px 16px 4px",
    padding: "10px 16px",
    maxWidth: "75%",
    marginBottom: 4,
    marginRight: "auto"
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
  // Show a single color bar for the most recent mood
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
  const [messages, setMessages] = useState([]); // { sender: "user"|"ai", text, label, confidence }
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [mood, setMood] = useState([]);
  const listRef = useRef(null);

  useEffect(() => {
    // Load chat history and mood history on mount
    apiRequest("/chat-history").then(res => {
      if (res.history) setMessages(res.history);
    });
    apiRequest("/mood-history").then(res => {
      if (res.mood) setMood(res.mood);
    });
  }, []);

  useEffect(() => {
    // Scroll to bottom on new message
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
        // Refresh mood history
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
        <Typography variant="h5" align="center" gutterBottom>Conversation</Typography>
        {error && <Alert severity="error">{error}</Alert>}
        {success && <Alert severity="success">{success}</Alert>}
        <MoodBar mood={mood} />
        <Paper variant="outlined" sx={{ height: 350, overflowY: "auto", p: 2, mb: 2, display: 'flex', flexDirection: 'column' }} ref={listRef}>
          {messages.map((msg, idx) => (
            <Box key={idx} sx={bubbleStyles[msg.sender]}>
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
          ))}
        </Paper>
        <Stack direction="row" spacing={2} mb={2}>
          <form onSubmit={handleSend} style={{ display: "flex", flex: 1, gap: 8 }}>
            <TextField
              label="Type your message..."
              value={input}
              onChange={e => setInput(e.target.value)}
              fullWidth
              autoFocus
            />
            <Button type="submit" variant="contained" color="primary">Send</Button>
          </form>
          <Button variant="outlined" color="secondary" onClick={handleClear} sx={{ minWidth: 120 }}>
            Clear Chat
          </Button>
        </Stack>
      </Box>
    </Container>
  );
} 