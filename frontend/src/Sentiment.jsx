import { useState } from "react";
import { TextField, Button, Container, Typography, Box, Alert } from "@mui/material";
import { apiRequest } from "./api";

export default function Sentiment() {
  const [text, setText] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setResult(null);
    try {
      const res = await apiRequest("/sentiment", "POST", { text });
      if (res.label) setResult(res);
      else setError(res.error || "Error analyzing sentiment");
    } catch {
      setError("Error analyzing sentiment");
    }
  };

  return (
    <Container maxWidth="sm">
      <Box mt={8}>
        <Typography variant="h5" align="center" gutterBottom>Sentiment Analysis</Typography>
        {error && <Alert severity="error">{error}</Alert>}
        <form onSubmit={handleSubmit}>
          <TextField
            label="Enter text"
            value={text}
            onChange={e => setText(e.target.value)}
            fullWidth margin="normal" required
          />
          <Button type="submit" variant="contained" color="primary" fullWidth sx={{ mt: 2 }}>
            Analyze
          </Button>
        </form>
        {result && (
          <Box mt={4}>
            <Alert severity="info">
              <strong>Label:</strong> {result.label}<br />
              <strong>Confidence:</strong> {result.confidence.toFixed(2)}
            </Alert>
          </Box>
        )}
      </Box>
    </Container>
  );
}
