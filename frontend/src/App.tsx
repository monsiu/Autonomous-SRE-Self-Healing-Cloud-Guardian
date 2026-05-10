import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import LiveLogStream from './components/LiveLogStream';
import AgentThinking from './components/AgentThinking';
import RemediationLog from './components/RemediationLog';
import IncidentTimeline from './components/IncidentTimeline';
import SystemHealthScore from './components/SystemHealthScore';
import StoredLogs from './components/StoredLogs';
import { useWebSocket } from './hooks/useWebSocket';
import { LogEntry, AgentState, RemediationAction, Incident, SystemHealth } from './types';

const API_BASE = 'http://localhost:8000';
const WS_BASE = 'ws://localhost:8000';

function App() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [activePanel, setActivePanel] = useState('health');
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [agentStates, setAgentStates] = useState<AgentState[]>([]);
  const [remediationActions, setRemediationActions] = useState<RemediationAction[]>([]);
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [healthHistory, setHealthHistory] = useState<Array<{ timestamp: string; score: number }>>([]);
  
  const [systemHealth, setSystemHealth] = useState<SystemHealth>({
    score: 95,
    trend: 'stable',
    metrics: {
      cpu: 45,
      memory: 62,
      errorRate: 0.5,
      responseTime: 120,
    },
    prediction: {
      nextHourScore: 93,
      confidence: 0.87,
    },
  });

  const { data: logData, isConnected: logsConnected } = useWebSocket<LogEntry>(`${WS_BASE}/ws/logs`);
  const { data: agentData, isConnected: agentsConnected } = useWebSocket<AgentState>(`${WS_BASE}/ws/agents`);

  // Calculate health score from real metrics
  const calculateHealthScore = (cpu: number, memory: number, errorRate: number): number => {
    // Health score based on actual metrics
    // CPU and Memory are inverted (high = bad)
    const cpuScore = Math.max(0, 100 - cpu);
    const memoryScore = Math.max(0, 100 - memory);
    const errorScore = Math.max(0, 100 - (errorRate * 10));
    
    // Weighted average: CPU 40%, Memory 30%, Errors 30%
    const score = (cpuScore * 0.4) + (memoryScore * 0.3) + (errorScore * 0.3);
    return Math.round(Math.max(0, Math.min(100, score)));
  };

  // Gradually decay error rate over time (errors become less relevant)
  useEffect(() => {
    const errorDecayInterval = setInterval(() => {
      setSystemHealth(prev => ({
        ...prev,
        metrics: {
          ...prev.metrics,
          errorRate: Math.max(0, prev.metrics.errorRate * 0.95), // 5% decay every interval
        },
      }));
    }, 10000); // Every 10 seconds

    return () => clearInterval(errorDecayInterval);
  }, []);

  // Fetch historical data on mount
  useEffect(() => {
    const fetchHistoricalData = async () => {
      try {
        // Fetch incident history
        const incidentsResponse = await fetch(`${API_BASE}/api/incidents/history`);
        if (incidentsResponse.ok) {
          const incidentsData = await incidentsResponse.json();
          if (incidentsData.incidents && Array.isArray(incidentsData.incidents)) {
            const formattedIncidents: Incident[] = incidentsData.incidents.map((inc: any) => ({
              id: inc.id || Date.now().toString(),
              type: inc.type || 'unknown',
              timestamp: inc.timestamp,
              resolved: true, // Historical incidents are resolved
              success: true,
              severity: inc.severity || 'medium',
              description: inc.description || 'Incident detected',
            }));
            setIncidents(formattedIncidents);
            console.log(`✅ Loaded ${formattedIncidents.length} historical incidents`);
          }
        }

        // Fetch remediation history
        const remediationsResponse = await fetch(`${API_BASE}/api/incidents/remediations`);
        if (remediationsResponse.ok) {
          const remediationsData = await remediationsResponse.json();
          if (remediationsData.remediations && Array.isArray(remediationsData.remediations)) {
            const formattedRemediations: RemediationAction[] = remediationsData.remediations.map((rem: any, idx: number) => {
              // Parse timestamp from format: 20260510_182130 to ISO format
              const timestampStr = rem.timestamp || '';
              let isoTimestamp = new Date().toISOString();
              
              if (timestampStr.match(/^\d{8}_\d{6}$/)) {
                // Format: YYYYMMDD_HHMMSS
                const year = timestampStr.substring(0, 4);
                const month = timestampStr.substring(4, 6);
                const day = timestampStr.substring(6, 8);
                const hour = timestampStr.substring(9, 11);
                const minute = timestampStr.substring(11, 13);
                const second = timestampStr.substring(13, 15);
                isoTimestamp = `${year}-${month}-${day}T${hour}:${minute}:${second}Z`;
              }
              
              return {
                id: `rem-${idx}`,
                action: `Generated post-mortem: ${rem.filename}`,
                timestamp: isoTimestamp,
                result: 'success',
                executionTime: 0,
                details: `Incident type: ${rem.incident_type}`,
              };
            });
            setRemediationActions(formattedRemediations);
            console.log(`✅ Loaded ${formattedRemediations.length} remediation actions`);
          }
        }
      } catch (error) {
        console.error('❌ Failed to fetch historical data:', error);
      }
    };

    fetchHistoricalData();
    
    // Fetch real metrics every 3 seconds and calculate health from them
    const metricsInterval = setInterval(async () => {
      try {
        const response = await fetch(`${API_BASE}/api/incidents/metrics`);
        if (response.ok) {
          const data = await response.json();
          if (data.available && data.metrics) {
            const cpu = Math.round(data.metrics.cpu_load);
            const memory = Math.round(data.metrics.ram_usage_percent);
            
            setSystemHealth(prev => {
              const newScore = calculateHealthScore(cpu, memory, prev.metrics.errorRate);
              const trend = newScore > prev.score + 2 ? 'improving' : 
                           newScore < prev.score - 2 ? 'degrading' : 'stable';
              
              // Predictive analysis: project score 1 hour ahead based on trend
              let nextHourScore = newScore;
              let confidence = 0.75;
              
              if (trend === 'improving') {
                // If improving, project continued improvement (but cap at 98)
                nextHourScore = Math.min(98, newScore + 10);
                confidence = 0.85;
              } else if (trend === 'degrading') {
                // If degrading, project continued degradation (but floor at 20)
                nextHourScore = Math.max(20, newScore - 15);
                confidence = 0.80;
              } else {
                // If stable, project slight improvement toward 95
                nextHourScore = newScore < 95 ? Math.min(95, newScore + 3) : newScore;
                confidence = 0.90;
              }
              
              return {
                ...prev,
                score: newScore,
                trend,
                metrics: {
                  ...prev.metrics,
                  cpu,
                  memory,
                },
                prediction: {
                  nextHourScore: Math.round(nextHourScore),
                  confidence,
                },
              };
            });
          }
        }
      } catch (error) {
        console.error('Failed to fetch real metrics:', error);
      }
    }, 3000);

    return () => clearInterval(metricsInterval);
  }, []); // Run once on mount

  useEffect(() => {
    if (logData) {
      setLogs(prev => [...prev.slice(-200), logData]);
      
      // Update error rate based on log severity
      if (logData.anomaly || logData.level === 'CRITICAL' || logData.level === 'ERROR') {
        setSystemHealth(prev => ({
          ...prev,
          metrics: {
            ...prev.metrics,
            errorRate: Math.min(10, prev.metrics.errorRate + 0.5),
          },
        }));
      }
    }
  }, [logData]);

  useEffect(() => {
    if (agentData) {
      const stateWithTimestamp = { ...agentData, timestamp: new Date().toISOString() };
      setAgentStates(prev => [...prev.slice(-10), stateWithTimestamp]);

      // Track remediation actions
      if (agentData.agent === 'Remediation Agent' && agentData.status === 'success') {
        const action: RemediationAction = {
          id: Date.now().toString(),
          action: agentData.message,
          timestamp: new Date().toISOString(),
          result: 'success',
          executionTime: agentData.details?.execution_time || 0,
          details: agentData.details?.result,
        };
        setRemediationActions(prev => [...prev, action]);
      }

      // Track incidents
      if (agentData.agent === 'Monitor Agent' && agentData.details?.diagnosis) {
        const incident: Incident = {
          id: Date.now().toString(),
          type: agentData.details.diagnosis,
          timestamp: new Date().toISOString(),
          resolved: false,
          success: false,
          severity: 'high',
          description: agentData.message,
        };
        setIncidents(prev => [...prev, incident]);
      }

      // Mark incident as resolved
      if (agentData.agent === 'Remediation Agent' && agentData.status === 'success') {
        setIncidents(prev => 
          prev.map((inc, idx) => 
            idx === prev.length - 1 
              ? { 
                  ...inc, 
                  resolved: true, 
                  success: true,
                  resolutionTime: agentData.details?.execution_time || 0 
                }
              : inc
          )
        );

        // Reduce error rate after successful remediation
        setSystemHealth(prev => ({
          ...prev,
          metrics: {
            ...prev.metrics,
            errorRate: Math.max(0, prev.metrics.errorRate - 1),
          },
        }));
      }
    }
  }, [agentData]);

  // Update health history
  useEffect(() => {
    const interval = setInterval(() => {
      const now = new Date();
      setHealthHistory(prev => [
        ...prev.slice(-20),
        {
          timestamp: now.toLocaleTimeString(),
          score: systemHealth.score,
        },
      ]);
    }, 5000);

    return () => clearInterval(interval);
  }, [systemHealth.score]);

  const handleTriggerIncident = async (type: string) => {
    try {
      const response = await fetch(`${API_BASE}/api/incidents/trigger`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ incident_type: type }),
      });
      
      if (!response.ok) {
        throw new Error(`Failed to trigger incident: ${response.statusText}`);
      }
      
      const data = await response.json();
      console.log('Incident triggered:', data);
    } catch (error) {
      console.error('Failed to trigger incident:', error);
      alert('Failed to trigger incident. Make sure the backend is running.');
    }
  };

  const handleStopIncident = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/incidents/stop`, {
        method: 'POST',
      });
      
      if (!response.ok) {
        throw new Error(`Failed to stop incident: ${response.statusText}`);
      }
      
      const data = await response.json();
      console.log('Incident stopped:', data);
    } catch (error) {
      console.error('Failed to stop incident:', error);
      alert('Failed to stop incident. Make sure the backend is running.');
    }
  };

  const isConnected = logsConnected && agentsConnected;

  const renderPanel = () => {
    switch (activePanel) {
      case 'logs':
        return <LiveLogStream logs={logs} />;
      case 'health':
        return <SystemHealthScore health={systemHealth} history={healthHistory} />;
      case 'agents':
        return <AgentThinking agentStates={agentStates} />;
      case 'remediation':
        return <RemediationLog actions={remediationActions} />;
      case 'incidents':
        return <IncidentTimeline incidents={incidents} />;
      case 'stored-logs':
        return <StoredLogs apiBase={API_BASE} />;
      default:
        return <SystemHealthScore health={systemHealth} history={healthHistory} />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-gray-100 flex">
      <Sidebar
        isOpen={isSidebarOpen}
        onClose={() => setIsSidebarOpen(false)}
        activePanel={activePanel}
        onPanelChange={setActivePanel}
      />

      <div className="flex-1 flex flex-col">
        <Header 
          isConnected={isConnected}
          onTriggerIncident={handleTriggerIncident}
          onStopIncident={handleStopIncident}
          onMenuClick={() => setIsSidebarOpen(!isSidebarOpen)}
        />

        <main className="flex-1 p-6">
          {/* Show active panel */}
          <div className="h-[calc(100vh-120px)]">
            {renderPanel()}
          </div>
        </main>
      </div>
    </div>
  );
}

export default App;
