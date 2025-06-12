import { useState } from "react";
import { TextField, Button, Container, Typography, Box, Alert } from "@mui/material";
import { apiRequest } from "./api";

export default function TTS() {
  const [text, setText] = useState("");
  const [audioUrl, setAudioUrl] = useState(null);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setAudioUrl(null);
    try {
      const blob = await apiRequest("/tts", "POST", { text }, true);
      setAudioUrl(URL.createObjectURL(blob));
    } catch {
      setError("Error generating speech");
    }
  };

  return (
    <Container maxWidth="sm">
      <Box mt={8}>
        <Typography variant="h5" align="center" gutterBottom>Text to Speech</Typography>
        {error && <Alert severity="error">{error}</Alert>}
        <form onSubmit={handleSubmit}>
          <TextField
            label="Enter text"
            value={text}
            onChange={e => setText(e.target.value)}
            fullWidth margin="normal" required
          />
          <Button type="submit" variant="contained" color="primary" fullWidth sx={{ mt: 2 }}>
            Synthesize
          </Button>
        </form>
        {audioUrl && (
          <Box mt={4} textAlign="center">
            <audio controls src={audioUrl} />
          </Box>
        )}
      </Box>
    </Container>
  );
}
