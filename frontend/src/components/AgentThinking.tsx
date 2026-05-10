import React from 'react';
import { Brain, CheckCircle, XCircle, Loader, TrendingUp } from 'lucide-react';
import { AgentState } from '../types';
import { format } from 'date-fns';

interface Props {
  agentStates: AgentState[];
}

const AgentThinking: React.FC<Props> = ({ agentStates }) => {
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'running': return <Loader className="w-5 h-5 text-blue-400 animate-spin" />;
      case 'success': return <CheckCircle className="w-5 h-5 text-green-400" />;
      case 'error': return <XCircle className="w-5 h-5 text-red-400" />;
      default: return <Brain className="w-5 h-5 text-gray-400" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running': return 'border-blue-500 bg-blue-900/20';
      case 'success': return 'border-green-500 bg-green-900/20';
      case 'error': return 'border-red-500 bg-red-900/20';
      default: return 'border-gray-600 bg-gray-800';
    }
  };

  return (
    <div className="bg-gray-800 rounded-lg shadow-xl p-4 h-full flex flex-col">
      <div className="flex items-center gap-2 mb-4">
        <Brain className="w-5 h-5 text-purple-400" />
        <h2 className="text-xl font-bold">Agent Thinking Display</h2>
      </div>

      <div className="flex-1 overflow-y-auto space-y-3">
        {agentStates.length === 0 ? (
          <div className="text-center text-gray-500 py-8">
            <Brain className="w-12 h-12 mx-auto mb-2 opacity-50" />
            <p>Waiting for agent activity...</p>
          </div>
        ) : (
          agentStates.map((state, idx) => (
            <div
              key={idx}
              className={`border-2 rounded-lg p-4 ${getStatusColor(state.status)}`}
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-2">
                  {getStatusIcon(state.status)}
                  <span className="font-semibold text-lg">{state.agent}</span>
                </div>
                {state.timestamp && (
                  <span className="text-xs text-gray-400">
                    {format(new Date(state.timestamp), 'HH:mm:ss')}
                  </span>
                )}
              </div>

              <p className="text-gray-300 mb-3">{state.message}</p>

              {state.details && (
                <div className="space-y-2 text-sm">
                  {/* Confidence Breakdown */}
                  {state.details.confidence !== undefined && (
                    <div className="flex items-center gap-2">
                      <TrendingUp className="w-4 h-4 text-blue-400" />
                      <span className="text-gray-400">Confidence:</span>
                      <div className="flex-1 bg-gray-700 rounded-full h-2">
                        <div
                          className="bg-blue-500 h-2 rounded-full transition-all"
                          style={{ width: `${state.details.confidence * 100}%` }}
                        />
                      </div>
                      <span className="text-blue-400 font-semibold">
                        {(state.details.confidence * 100).toFixed(0)}%
                      </span>
                    </div>
                  )}

                  {/* Detailed Confidence Breakdown */}
                  {state.details.confidence_breakdown && (
                    <div className="bg-gray-900/50 p-3 rounded">
                      <p className="text-gray-400 text-xs mb-2">Confidence Breakdown:</p>
                      <div className="space-y-1">
                        <div className="flex justify-between text-xs">
                          <span className="text-gray-400">Pattern Match:</span>
                          <span className="text-blue-400">{(state.details.confidence_breakdown.pattern_match * 100).toFixed(0)}%</span>
                        </div>
                        <div className="flex justify-between text-xs">
                          <span className="text-gray-400">Similarity Score:</span>
                          <span className="text-purple-400">{(state.details.confidence_breakdown.similarity_score * 100).toFixed(0)}%</span>
                        </div>
                        <div className="flex justify-between text-xs font-semibold border-t border-gray-700 pt-1 mt-1">
                          <span className="text-gray-300">Final Confidence:</span>
                          <span className="text-green-400">{(state.details.confidence_breakdown.final_confidence * 100).toFixed(0)}%</span>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Similar Incidents with Enhanced Display */}
                  {state.details.similar_incidents && state.details.similar_incidents.length > 0 && (
                    <div className="bg-gray-900/50 p-3 rounded">
                      <p className="text-gray-400 text-xs mb-2">
                        Similar Incidents Found ({state.details.similar_count || state.details.similar_incidents.length}):
                      </p>
                      <div className="space-y-2">
                        {state.details.similar_incidents.map((incident: any, i: number) => (
                          <div key={i} className="border-l-2 border-cyan-500 pl-2 py-1">
                            <div className="flex items-center justify-between mb-1">
                              <span className="text-cyan-400 font-semibold text-xs">
                                {incident.type || incident.incident_type || 'Unknown'}
                              </span>
                              <span className="text-gray-400 text-xs">
                                {incident.match_score ? `${(incident.match_score * 100).toFixed(0)}%` : 
                                 incident.similarity ? `${(incident.similarity * 100).toFixed(0)}%` : 'N/A'} match
                              </span>
                            </div>
                            {incident.severity && (
                              <span className={`text-xs px-2 py-0.5 rounded ${
                                incident.severity === 'critical' ? 'bg-red-900/50 text-red-400' :
                                incident.severity === 'high' ? 'bg-orange-900/50 text-orange-400' :
                                'bg-yellow-900/50 text-yellow-400'
                              }`}>
                                {incident.severity}
                              </span>
                            )}
                            {incident.description && (
                              <p className="text-gray-500 text-xs mt-1">{incident.description}</p>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Top Similar Incidents (alternative format) */}
                  {state.details.top_similar_incidents && state.details.top_similar_incidents.length > 0 && (
                    <div className="bg-gray-900/50 p-3 rounded">
                      <p className="text-gray-400 text-xs mb-2">Top Matching Incidents:</p>
                      <div className="space-y-1">
                        {state.details.top_similar_incidents.map((incident: any, i: number) => (
                          <div key={i} className="flex items-center justify-between text-xs">
                            <span className="text-cyan-400">{incident.type}</span>
                            <span className="text-gray-400">
                              {(incident.match_score * 100).toFixed(0)}% match
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Reasoning */}
                  {state.details.reasoning && (
                    <div className="bg-gray-900/50 p-3 rounded">
                      <p className="text-gray-400 text-xs mb-1">Reasoning:</p>
                      <p className="text-gray-200 text-xs">{state.details.reasoning}</p>
                    </div>
                  )}

                  {state.details.diagnosis && (
                    <div className="bg-gray-900/50 p-3 rounded">
                      <p className="text-gray-400 text-xs mb-1">Diagnosis:</p>
                      <p className="text-gray-200">{state.details.diagnosis}</p>
                    </div>
                  )}

                  {state.details.remediation_plan && (
                    <div className="bg-gray-900/50 p-3 rounded">
                      <p className="text-gray-400 text-xs mb-1">Remediation Plan:</p>
                      <p className="text-gray-200">{state.details.remediation_plan}</p>
                    </div>
                  )}

                  {state.details.execution_time !== undefined && (
                    <div className="flex items-center gap-2 text-xs text-gray-400">
                      <span>Execution Time:</span>
                      <span className="text-green-400 font-semibold">
                        {state.details.execution_time.toFixed(2)}s
                      </span>
                    </div>
                  )}

                  {state.details.result && (
                    <div className="bg-gray-900/50 p-3 rounded">
                      <p className="text-gray-400 text-xs mb-1">Result:</p>
                      <p className="text-gray-200">{state.details.result}</p>
                    </div>
                  )}

                  {/* Diagnosis Method */}
                  {state.details.diagnosis_method && (
                    <div className="text-xs text-gray-500 italic mt-2">
                      Method: {state.details.diagnosis_method}
                    </div>
                  )}
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default AgentThinking;
