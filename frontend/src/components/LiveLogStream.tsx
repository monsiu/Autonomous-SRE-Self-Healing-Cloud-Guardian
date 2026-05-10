import React, { useState, useEffect, useRef } from 'react';
import { AlertCircle, Filter, Terminal } from 'lucide-react';
import { LogEntry } from '../types';
import { format } from 'date-fns';

interface Props {
  logs: LogEntry[];
}

const LiveLogStream: React.FC<Props> = ({ logs }) => {
  const [filter, setFilter] = useState<string>('');
  const [severityFilter, setSeverityFilter] = useState<string>('all');
  const [showAnomaliesOnly, setShowAnomaliesOnly] = useState(false);
  const logEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  const filteredLogs = logs.filter(log => {
    if (showAnomaliesOnly && !log.anomaly) return false;
    if (severityFilter !== 'all' && log.level !== severityFilter) return false;
    if (filter && !log.message.toLowerCase().includes(filter.toLowerCase()) && 
        !log.service.toLowerCase().includes(filter.toLowerCase())) return false;
    return true;
  });

  const getSeverityColor = (level: string, anomaly?: boolean) => {
    if (anomaly) return 'text-red-400 bg-red-900/30 border-red-500';
    switch (level) {
      case 'CRITICAL': return 'text-red-400 bg-red-900/20';
      case 'ERROR': return 'text-orange-400 bg-orange-900/20';
      case 'WARNING': return 'text-yellow-400 bg-yellow-900/20';
      case 'INFO': return 'text-blue-400 bg-blue-900/20';
      default: return 'text-gray-400 bg-gray-800';
    }
  };

  return (
    <div className="bg-gray-800 rounded-lg shadow-xl p-4 h-full flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Terminal className="w-5 h-5 text-green-400" />
          <h2 className="text-xl font-bold">Live Log Stream</h2>
          <span className="text-sm text-gray-400">({filteredLogs.length} logs)</span>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowAnomaliesOnly(!showAnomaliesOnly)}
            className={`px-3 py-1 rounded text-sm ${
              showAnomaliesOnly ? 'bg-red-600 text-white' : 'bg-gray-700 text-gray-300'
            }`}
          >
            <AlertCircle className="w-4 h-4 inline mr-1" />
            Anomalies Only
          </button>
        </div>
      </div>

      <div className="flex gap-2 mb-3">
        <div className="flex-1 relative">
          <Filter className="w-4 h-4 absolute left-3 top-2.5 text-gray-400" />
          <input
            type="text"
            placeholder="Filter logs..."
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="w-full pl-10 pr-3 py-2 bg-gray-700 border border-gray-600 rounded text-sm focus:outline-none focus:border-blue-500"
          />
        </div>
        <select
          value={severityFilter}
          onChange={(e) => setSeverityFilter(e.target.value)}
          className="px-3 py-2 bg-gray-700 border border-gray-600 rounded text-sm focus:outline-none focus:border-blue-500"
        >
          <option value="all">All Levels</option>
          <option value="INFO">INFO</option>
          <option value="WARNING">WARNING</option>
          <option value="ERROR">ERROR</option>
          <option value="CRITICAL">CRITICAL</option>
        </select>
      </div>

      <div className="flex-1 overflow-y-auto space-y-1 font-mono text-sm">
        {filteredLogs.map((log, idx) => (
          <div
            key={idx}
            className={`p-2 rounded border-l-4 ${getSeverityColor(log.level, log.anomaly)} ${
              log.anomaly ? 'border-l-4 animate-pulse' : 'border-l-0'
            }`}
          >
            <div className="flex items-start gap-2">
              <span className="text-gray-500 text-xs whitespace-nowrap">
                {format(new Date(log.timestamp), 'HH:mm:ss.SSS')}
              </span>
              <span className={`px-2 py-0.5 rounded text-xs font-semibold ${getSeverityColor(log.level)}`}>
                {log.level}
              </span>
              <span className="text-cyan-400 text-xs">[{log.service}]</span>
              <span className="text-gray-300 flex-1">{log.message}</span>
              {log.anomaly && (
                <AlertCircle className="w-4 h-4 text-red-400 flex-shrink-0" />
              )}
            </div>
          </div>
        ))}
        <div ref={logEndRef} />
      </div>
    </div>
  );
};

export default LiveLogStream;
