import React, { useState } from 'react';
import {
  Box,
  Container,
  Typography,
  TextField,
  Button,
  Card,
  CardContent,
  Grid,
  Chip,
  Alert,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Rating,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  Search as SearchIcon,
  LocalHospital as HospitalIcon,
  AttachMoney as MoneyIcon,
  HealthAndSafety as HealthIcon,
  Phone as PhoneIcon,
  LocationOn as LocationIcon,
  Info as InfoIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { apiCall } from './api';

const HealthcareNavigation = () => {
  const [activeTab, setActiveTab] = useState('symptoms');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Form states
  const [symptoms, setSymptoms] = useState('');
  const [specialty, setSpecialty] = useState('');
  const [location, setLocation] = useState('');
  const [insurance, setInsurance] = useState('');
  const [service, setService] = useState('');

  // Results states
  const [symptomAnalysis, setSymptomAnalysis] = useState(null);
  const [providers, setProviders] = useState([]);
  const [costEstimate, setCostEstimate] = useState(null);

  const handleSymptomAnalysis = async () => {
    if (!symptoms.trim()) {
      setError('Please enter your symptoms');
      return;
    }

    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const response = await apiCall('/analyze-symptoms', 'POST', {
        symptoms: symptoms
      });

      if (response.success) {
        setSymptomAnalysis(response.analysis);
        setSuccess('Symptom analysis completed successfully');
      } else {
        setError('Failed to analyze symptoms');
      }
    } catch (err) {
      setError('Error analyzing symptoms: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleFindDoctors = async () => {
    if (!specialty.trim() || !location.trim()) {
      setError('Please enter both specialty and location');
      return;
    }

    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const response = await apiCall('/find-doctors', 'POST', {
        specialty: specialty,
        location: location,
        insurance: insurance || null
      });

      if (response.success) {
        setProviders(response.providers);
        setSuccess(`Found ${response.count} providers`);
      } else {
        setError('Failed to find doctors');
      }
    } catch (err) {
      setError('Error finding doctors: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleEstimateCosts = async () => {
    if (!service.trim() || !location.trim()) {
      setError('Please enter both service and location');
      return;
    }

    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const response = await apiCall('/estimate-costs', 'POST', {
        service: service,
        location: location,
        insurance: insurance || null
      });

      if (response.success) {
        setCostEstimate(response.cost_estimate);
        setSuccess('Cost estimate completed successfully');
      } else {
        setError('Failed to estimate costs');
      }
    } catch (err) {
      setError('Error estimating costs: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <Typography variant="h3" component="h1" gutterBottom align="center" sx={{ mb: 4 }}>
          🏥 Healthcare Navigation
        </Typography>
        <Typography variant="h6" align="center" color="text.secondary" sx={{ mb: 4 }}>
          AI-powered healthcare provider finder and symptom analyzer
        </Typography>
      </motion.div>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 2 }}>
          {success}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Navigation Tabs */}
        <Grid item xs={12}>
          <Box sx={{ display: 'flex', gap: 1, mb: 3, flexWrap: 'wrap' }}>
            {[
              { key: 'symptoms', label: 'Symptom Analysis', icon: <HealthIcon /> },
              { key: 'doctors', label: 'Find Doctors', icon: <HospitalIcon /> },
              { key: 'costs', label: 'Estimate Costs', icon: <MoneyIcon /> }
            ].map((tab) => (
              <Button
                key={tab.key}
                variant={activeTab === tab.key ? 'contained' : 'outlined'}
                startIcon={tab.icon}
                onClick={() => setActiveTab(tab.key)}
              >
                {tab.label}
              </Button>
            ))}
          </Box>
        </Grid>

        {/* Input Forms */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              {activeTab === 'symptoms' && (
                <>
                  <Typography variant="h6" gutterBottom>
                    <HealthIcon sx={{ mr: 1 }} />
                    Symptom Analysis
                  </Typography>
                  <TextField
                    fullWidth
                    multiline
                    rows={4}
                    label="Describe your symptoms"
                    value={symptoms}
                    onChange={(e) => setSymptoms(e.target.value)}
                    sx={{ mb: 2 }}
                    placeholder="e.g., I've been experiencing headaches and fatigue..."
                  />
                  <Button
                    fullWidth
                    variant="contained"
                    onClick={handleSymptomAnalysis}
                    disabled={loading}
                    startIcon={loading ? <CircularProgress size={20} /> : <SearchIcon />}
                  >
                    Analyze Symptoms
                  </Button>
                </>
              )}

              {activeTab === 'doctors' && (
                <>
                  <Typography variant="h6" gutterBottom>
                    <HospitalIcon sx={{ mr: 1 }} />
                    Find Healthcare Providers
                  </Typography>
                  <TextField
                    fullWidth
                    label="Specialty"
                    value={specialty}
                    onChange={(e) => setSpecialty(e.target.value)}
                    sx={{ mb: 2 }}
                    placeholder="e.g., therapist, psychiatrist..."
                  />
                  <TextField
                    fullWidth
                    label="Location"
                    value={location}
                    onChange={(e) => setLocation(e.target.value)}
                    sx={{ mb: 2 }}
                    placeholder="e.g., New York, NY"
                  />
                  <TextField
                    fullWidth
                    label="Insurance (optional)"
                    value={insurance}
                    onChange={(e) => setInsurance(e.target.value)}
                    sx={{ mb: 2 }}
                    placeholder="e.g., Blue Cross Blue Shield"
                  />
                  <Button
                    fullWidth
                    variant="contained"
                    onClick={handleFindDoctors}
                    disabled={loading}
                    startIcon={loading ? <CircularProgress size={20} /> : <SearchIcon />}
                  >
                    Find Providers
                  </Button>
                </>
              )}

              {activeTab === 'costs' && (
                <>
                  <Typography variant="h6" gutterBottom>
                    <MoneyIcon sx={{ mr: 1 }} />
                    Estimate Healthcare Costs
                  </Typography>
                  <TextField
                    fullWidth
                    label="Service"
                    value={service}
                    onChange={(e) => setService(e.target.value)}
                    sx={{ mb: 2 }}
                    placeholder="e.g., therapy, psychiatry..."
                  />
                  <TextField
                    fullWidth
                    label="Location"
                    value={location}
                    onChange={(e) => setLocation(e.target.value)}
                    sx={{ mb: 2 }}
                    placeholder="e.g., New York, NY"
                  />
                  <TextField
                    fullWidth
                    label="Insurance (optional)"
                    value={insurance}
                    onChange={(e) => setInsurance(e.target.value)}
                    sx={{ mb: 2 }}
                    placeholder="e.g., Blue Cross Blue Shield"
                  />
                  <Button
                    fullWidth
                    variant="contained"
                    onClick={handleEstimateCosts}
                    disabled={loading}
                    startIcon={loading ? <CircularProgress size={20} /> : <MoneyIcon />}
                  >
                    Estimate Costs
                  </Button>
                </>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Results Display */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Results
              </Typography>

              {/* Symptom Analysis Results */}
              {symptomAnalysis && (
                <Box sx={{ mb: 3 }}>
                  <Typography variant="subtitle1" gutterBottom>
                    Symptom Analysis
                  </Typography>
                  <Chip
                    icon={<WarningIcon />}
                    label={`Urgency: ${symptomAnalysis.urgency_level}`}
                    color={symptomAnalysis.urgency_level === 'high' ? 'error' : 'warning'}
                    sx={{ mb: 2 }}
                  />
                  
                  <Typography variant="subtitle2" gutterBottom>Recommended Providers:</Typography>
                  <Box sx={{ mb: 2 }}>
                    {symptomAnalysis.recommended_providers?.map((provider, index) => (
                      <Chip key={index} label={provider} sx={{ mr: 1, mb: 1 }} />
                    ))}
                  </Box>

                  <Typography variant="subtitle2" gutterBottom>Self-Care Tips:</Typography>
                  <List dense>
                    {symptomAnalysis.self_care_tips?.map((tip, index) => (
                      <ListItem key={index}>
                        <ListItemIcon><CheckCircleIcon /></ListItemIcon>
                        <ListItemText primary={tip} />
                      </ListItem>
                    ))}
                  </List>
                </Box>
              )}

              {/* Provider Results */}
              {providers.length > 0 && (
                <Box sx={{ mb: 3 }}>
                  <Typography variant="subtitle1" gutterBottom>
                    Healthcare Providers ({providers.length})
                  </Typography>
                  <List>
                    {providers.map((provider, index) => (
                      <ListItem key={index}>
                        <ListItemIcon><HospitalIcon /></ListItemIcon>
                        <ListItemText
                          primary={provider.name}
                          secondary={
                            <Box>
                              <Typography variant="body2" color="text.secondary">
                                {provider.specialty} • {provider.location}
                              </Typography>
                              <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                                <Rating value={provider.rating} readOnly size="small" />
                                <Typography variant="body2" sx={{ ml: 1 }}>
                                  {provider.rating}/5
                                </Typography>
                              </Box>
                              <Typography variant="body2" color="text.secondary">
                                Cost: {provider.estimated_cost}
                              </Typography>
                            </Box>
                          }
                        />
                        <Tooltip title="Call Provider">
                          <IconButton color="primary">
                            <PhoneIcon />
                          </IconButton>
                        </Tooltip>
                      </ListItem>
                    ))}
                  </List>
                </Box>
              )}

              {/* Cost Estimate Results */}
              {costEstimate && (
                <Box>
                  <Typography variant="subtitle1" gutterBottom>
                    Cost Estimate
                  </Typography>
                  <List dense>
                    <ListItem>
                      <ListItemIcon><MoneyIcon /></ListItemIcon>
                      <ListItemText 
                        primary={`Service: ${costEstimate.service}`}
                        secondary={`Location: ${costEstimate.location}`}
                      />
                    </ListItem>
                    <ListItem>
                      <ListItemIcon><MoneyIcon /></ListItemIcon>
                      <ListItemText primary={`Cost Range: ${costEstimate.cost_range}`} />
                    </ListItem>
                    <ListItem>
                      <ListItemIcon><MoneyIcon /></ListItemIcon>
                      <ListItemText primary={`Average Cost: ${costEstimate.average_cost}`} />
                    </ListItem>
                  </List>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
};

export default HealthcareNavigation; 