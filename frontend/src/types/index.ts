export interface LogEntry {
  timestamp: string;
  level: 'INFO' | 'WARNING' | 'ERROR' | 'CRITICAL';
  service: string;
  message: string;
  anomaly?: boolean;
  metadata?: Record<string, any>;
}

export interface AgentState {
  agent: string;
  status: 'idle' | 'running' | 'success' | 'error';
  message: string;
  details?: {
    confidence?: number;
    similar_incidents?: Array<{
      incident_type: string;
      similarity: number;
      timestamp: string;
    }>;
    diagnosis?: string;
    remediation_plan?: string;
    execution_time?: number;
    result?: string;
  };
  timestamp?: string;
}

export interface RemediationAction {
  id: string;
  action: string;
  timestamp: string;
  result: 'success' | 'failure' | 'pending';
  executionTime: number;
  details?: string;
}

export interface Incident {
  id: string;
  type: string;
  timestamp: string;
  resolved: boolean;
  resolutionTime?: number;
  success: boolean;
  severity: 'low' | 'medium' | 'high' | 'critical';
  description: string;
}

export interface SystemHealth {
  score: number;
  trend: 'improving' | 'stable' | 'degrading';
  metrics: {
    cpu: number;
    memory: number;
    errorRate: number;
    responseTime: number;
  };
  prediction: {
    nextHourScore: number;
    confidence: number;
  };
}
