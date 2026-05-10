import React from 'react';
import { History, CheckCircle, XCircle, AlertTriangle } from 'lucide-react';
import { Incident } from '../types';
import { format } from 'date-fns';

interface Props {
  incidents: Incident[];
}

const IncidentTimeline: React.FC<Props> = ({ incidents }) => {
  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'text-red-400 bg-red-900/30 border-red-500';
      case 'high': return 'text-orange-400 bg-orange-900/30 border-orange-500';
      case 'medium': return 'text-yellow-400 bg-yellow-900/30 border-yellow-500';
      default: return 'text-blue-400 bg-blue-900/30 border-blue-500';
    }
  };

  const stats = {
    total: incidents.length,
    resolved: incidents.filter(i => i.resolved).length,
    avgResolutionTime: incidents.filter(i => i.resolutionTime).reduce((acc, i) => acc + (i.resolutionTime || 0), 0) / incidents.filter(i => i.resolutionTime).length || 0,
    successRate: incidents.length > 0 ? (incidents.filter(i => i.success).length / incidents.length) * 100 : 0,
  };

  return (
    <div className="bg-gray-800 rounded-lg shadow-xl p-4 h-full flex flex-col">
      <div className="flex items-center gap-2 mb-4">
        <History className="w-5 h-5 text-indigo-400" />
        <h2 className="text-xl font-bold">Incident History Timeline</h2>
      </div>

      <div className="grid grid-cols-4 gap-3 mb-4">
        <div className="bg-gray-900/50 p-3 rounded">
          <p className="text-xs text-gray-400 mb-1">Total Incidents</p>
          <p className="text-2xl font-bold text-blue-400">{stats.total}</p>
        </div>
        <div className="bg-gray-900/50 p-3 rounded">
          <p className="text-xs text-gray-400 mb-1">Resolved</p>
          <p className="text-2xl font-bold text-green-400">{stats.resolved}</p>
        </div>
        <div className="bg-gray-900/50 p-3 rounded">
          <p className="text-xs text-gray-400 mb-1">Avg Resolution</p>
          <p className="text-2xl font-bold text-purple-400">{stats.avgResolutionTime.toFixed(1)}s</p>
        </div>
        <div className="bg-gray-900/50 p-3 rounded">
          <p className="text-xs text-gray-400 mb-1">Success Rate</p>
          <p className="text-2xl font-bold text-cyan-400">{stats.successRate.toFixed(0)}%</p>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto">
        {incidents.length === 0 ? (
          <div className="text-center text-gray-500 py-8">
            <History className="w-12 h-12 mx-auto mb-2 opacity-50" />
            <p>No incidents recorded</p>
          </div>
        ) : (
          <div className="space-y-3">
            {incidents.map((incident) => (
              <div
                key={incident.id}
                className={`border-l-4 rounded-lg p-4 ${getSeverityColor(incident.severity)}`}
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <AlertTriangle className={`w-5 h-5 ${getSeverityColor(incident.severity).split(' ')[0]}`} />
                    <h3 className="font-semibold">{incident.type}</h3>
                    <span className={`px-2 py-0.5 rounded text-xs font-semibold ${getSeverityColor(incident.severity)}`}>
                      {incident.severity.toUpperCase()}
                    </span>
                  </div>
                  {incident.resolved ? (
                    <CheckCircle className="w-5 h-5 text-green-400" />
                  ) : (
                    <XCircle className="w-5 h-5 text-red-400" />
                  )}
                </div>

                <p className="text-sm text-gray-300 mb-2">{incident.description}</p>

                <div className="flex items-center gap-4 text-xs text-gray-400">
                  <span>{format(new Date(incident.timestamp), 'MMM dd, yyyy HH:mm:ss')}</span>
                  {incident.resolutionTime && (
                    <span className="text-green-400">
                      Resolved in {incident.resolutionTime.toFixed(2)}s
                    </span>
                  )}
                  <span className={incident.success ? 'text-green-400' : 'text-red-400'}>
                    {incident.success ? 'Success' : 'Failed'}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default IncidentTimeline;
