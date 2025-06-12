import { useState, useRef, useEffect } from "react";
import { TextField, Button, Container, Typography, Box, Paper, List, ListItem, ListItemText, Chip, Alert } from "@mui/material";
import { apiRequest } from "./api";

export default function Conversation() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]); // { sender: "user"|"ai", text, label, confidence }
  const [error, setError] = useState("");
  const listRef = useRef(null);

  useEffect(() => {
    // Load chat history on mount
    apiRequest("/chat-history").then(res => {
      if (res.history) setMessages(res.history);
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
      } else {
        setError(res.error || "Error getting AI response");
      }
    } catch {
      setError("Error getting AI response");
    }
  };

  return (
    <Container maxWidth="sm">
      <Box mt={8}>
        <Typography variant="h5" align="center" gutterBottom>Conversation</Typography>
        {error && <Alert severity="error">{error}</Alert>}
        <Paper variant="outlined" sx={{ height: 350, overflowY: "auto", p: 2, mb: 2 }} ref={listRef}>
          <List>
            {messages.map((msg, idx) => (
              <ListItem key={idx} alignItems="flex-start">
                <ListItemText
                  primary={
                    <>
                      <strong>{msg.sender === "user" ? "You" : "AI"}:</strong> {msg.text}
                      {msg.label && (
                        <Chip
                          label={`${msg.label} (${(msg.confidence * 100).toFixed(0)}%)`}
                          size="small"
                          color={msg.label === "positive" ? "success" : msg.label === "negative" ? "error" : "default"}
                          sx={{ ml: 1 }}
                        />
                      )}
                    </>
                  }
                />
              </ListItem>
            ))}
          </List>
        </Paper>
        <form onSubmit={handleSend} style={{ display: "flex", gap: 8 }}>
          <TextField
            label="Type your message..."
            value={input}
            onChange={e => setInput(e.target.value)}
            fullWidth
            autoFocus
          />
          <Button type="submit" variant="contained" color="primary">Send</Button>
        </form>
      </Box>
    </Container>
  );
} 