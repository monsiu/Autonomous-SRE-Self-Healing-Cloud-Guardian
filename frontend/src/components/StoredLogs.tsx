import React, { useState, useEffect } from 'react';
import { Database, AlertCircle, Info, AlertTriangle, XCircle } from 'lucide-react';

interface StoredLog {
  id: string;
  timestamp: string;
  level: 'INFO' | 'WARNING' | 'ERROR' | 'CRITICAL';
  service: string;
  message: string;
  source: string;
  anomaly: boolean;
}

interface Props {
  apiBase: string;
}

const StoredLogs: React.FC<Props> = ({ apiBase }) => {
  const [logs, setLogs] = useState<StoredLog[]>([]);
  const [totalLogs, setTotalLogs] = useState(0);
  const [loading, setLoading] = useState(true);
  const [filterLevel, setFilterLevel] = useState<string>('ALL');
  const [filterService, setFilterService] = useState<string>('ALL');

  useEffect(() => {
    fetchLogs();
    const interval = setInterval(fetchLogs, 5000); // Refresh every 5 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchLogs = async () => {
    try {
      const response = await fetch(`${apiBase}/api/incidents/logs`);
      if (response.ok) {
        const data = await response.json();
        setLogs(data.logs || []);
        setTotalLogs(data.total || 0);
      }
    } catch (error) {
      console.error('Failed to fetch logs:', error);
    } finally {
      setLoading(false);
    }
  };

  const getLevelIcon = (level: string) => {
    switch (level) {
      case 'CRITICAL':
        return <XCircle className="w-4 h-4 text-red-500" />;
      case 'ERROR':
        return <AlertCircle className="w-4 h-4 text-red-400" />;
      case 'WARNING':
        return <AlertTriangle className="w-4 h-4 text-yellow-400" />;
      default:
        return <Info className="w-4 h-4 text-blue-400" />;
    }
  };

  const getLevelColor = (level: string) => {
    switch (level) {
      case 'CRITICAL':
        return 'text-red-500 bg-red-900/20';
      case 'ERROR':
        return 'text-red-400 bg-red-900/20';
      case 'WARNING':
        return 'text-yellow-400 bg-yellow-900/20';
      default:
        return 'text-blue-400 bg-blue-900/20';
    }
  };

  const filteredLogs = logs.filter(log => {
    if (filterLevel !== 'ALL' && log.level !== filterLevel) return false;
    if (filterService !== 'ALL' && log.service !== filterService) return false;
    return true;
  });

  const uniqueServices = Array.from(new Set(logs.map(log => log.service)));

  if (loading) {
    return (
      <div className="bg-gray-800 rounded-lg shadow-xl p-6 h-full flex items-center justify-center">
        <p className="text-gray-400">Loading logs...</p>
      </div>
    );
  }

  return (
    <div className="bg-gray-800 rounded-lg shadow-xl p-4 h-full flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Database className="w-5 h-5 text-purple-400" />
          <h2 className="text-xl font-bold">Stored Logs</h2>
          <span className="text-sm text-gray-400">({totalLogs} total)</span>
        </div>

        <div className="flex gap-2">
          <select
            value={filterLevel}
            onChange={(e) => setFilterLevel(e.target.value)}
            className="px-3 py-1 bg-gray-700 border border-gray-600 rounded text-sm"
          >
            <option value="ALL">All Levels</option>
            <option value="CRITICAL">Critical</option>
            <option value="ERROR">Error</option>
            <option value="WARNING">Warning</option>
            <option value="INFO">Info</option>
          </select>

          <select
            value={filterService}
            onChange={(e) => setFilterService(e.target.value)}
            className="px-3 py-1 bg-gray-700 border border-gray-600 rounded text-sm"
          >
            <option value="ALL">All Services</option>
            {uniqueServices.map(service => (
              <option key={service} value={service}>{service}</option>
            ))}
          </select>
        </div>
      </div>

      <div className="flex-1 overflow-auto">
        <table className="w-full text-sm">
          <thead className="sticky top-0 bg-gray-900 border-b border-gray-700">
            <tr>
              <th className="text-left p-2 text-gray-400 font-semibold">Time</th>
              <th className="text-left p-2 text-gray-400 font-semibold">Level</th>
              <th className="text-left p-2 text-gray-400 font-semibold">Service</th>
              <th className="text-left p-2 text-gray-400 font-semibold">Source</th>
              <th className="text-left p-2 text-gray-400 font-semibold">Message</th>
            </tr>
          </thead>
          <tbody>
            {filteredLogs.length === 0 ? (
              <tr>
                <td colSpan={5} className="text-center p-8 text-gray-500">
                  No logs found
                </td>
              </tr>
            ) : (
              filteredLogs.map((log) => (
                <tr
                  key={log.id}
                  className={`border-b border-gray-700/50 hover:bg-gray-700/30 transition-colors ${
                    log.anomaly ? 'bg-red-900/10' : ''
                  }`}
                >
                  <td className="p-2 text-gray-400 whitespace-nowrap">
                    {new Date(log.timestamp).toLocaleTimeString()}
                  </td>
                  <td className="p-2">
                    <div className="flex items-center gap-2">
                      {getLevelIcon(log.level)}
                      <span className={`px-2 py-0.5 rounded text-xs font-semibold ${getLevelColor(log.level)}`}>
                        {log.level}
                      </span>
                    </div>
                  </td>
                  <td className="p-2 text-gray-300">{log.service}</td>
                  <td className="p-2 text-gray-400 text-xs">{log.source}</td>
                  <td className="p-2 text-gray-300">
                    {log.message}
                    {log.anomaly && (
                      <span className="ml-2 px-2 py-0.5 bg-red-900/30 text-red-400 rounded text-xs">
                        ANOMALY
                      </span>
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      <div className="mt-3 pt-3 border-t border-gray-700 text-xs text-gray-500">
        Showing {filteredLogs.length} of {logs.length} logs (last 100 from vector store)
      </div>
    </div>
  );
};

export default StoredLogs;
