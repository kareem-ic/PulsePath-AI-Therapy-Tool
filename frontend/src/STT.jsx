import { useState } from "react";
import { Button, Container, Typography, Box, Alert } from "@mui/material";
import { apiRequest } from "./api";

export default function STT() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState("");
  const [error, setError] = useState("");

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setResult("");
    setError("");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setResult("");
    setError("");
    if (!file) {
      setError("Please upload a WAV file.");
      return;
    }
    try {
      const arrayBuffer = await file.arrayBuffer();
      const base64Audio = btoa(
        new Uint8Array(arrayBuffer).reduce((data, byte) => data + String.fromCharCode(byte), "")
      );
      const res = await apiRequest("/stt", "POST", { audio: base64Audio });
      if (res.text) setResult(res.text);
      else setError(res.error || "Error transcribing audio");
    } catch {
      setError("Error transcribing audio");
    }
  };

  return (
    <Container maxWidth="sm">
      <Box mt={8}>
        <Typography variant="h5" align="center" gutterBottom>Speech to Text</Typography>
        {error && <Alert severity="error">{error}</Alert>}
        <form onSubmit={handleSubmit}>
          <Button variant="contained" component="label" fullWidth sx={{ mt: 2 }}>
            Upload WAV File
            <input type="file" accept=".wav,audio/wav" hidden onChange={handleFileChange} />
          </Button>
          <Button type="submit" variant="contained" color="primary" fullWidth sx={{ mt: 2 }}>
            Transcribe
          </Button>
        </form>
        {result && (
          <Box mt={4}>
            <Alert severity="info" sx={{ whiteSpace: 'pre-wrap' }}>{result}</Alert>
          </Box>
        )}
      </Box>
    </Container>
  );
}


