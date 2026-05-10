import React, { useState } from 'react';
import { Shield, Wifi, WifiOff, Menu, Play, Square, AlertTriangle } from 'lucide-react';

interface Props {
  isConnected: boolean;
  onTriggerIncident: (type: string) => void;
  onStopIncident: () => void;
  onMenuClick: () => void;
}

const Header: React.FC<Props> = ({ isConnected, onTriggerIncident, onStopIncident, onMenuClick }) => {
  const [selectedIncident, setSelectedIncident] = useState<string>('ddos');
  const [isIncidentActive, setIsIncidentActive] = useState(false);

  const incidentLabels: Record<string, string> = {
    ddos: 'DDoS Attack',
    cpu_surge: 'CPU Surge',
    db_bottleneck: 'DB Bottleneck',
  };

  const handleStart = () => {
    onTriggerIncident(selectedIncident);
    setIsIncidentActive(true);
  };

  const handleStop = () => {
    onStopIncident();
    setIsIncidentActive(false);
  };

  return (
    <header className="bg-gray-800 border-b border-gray-700 px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <button
            onClick={onMenuClick}
            className="p-2 hover:bg-gray-700 rounded transition-colors"
            aria-label="Toggle menu"
          >
            <Menu className="w-6 h-6 text-gray-300" />
          </button>
          <Shield className="w-8 h-8 text-blue-400" />
          <div>
            <h1 className="text-2xl font-bold text-white">Autonomous SRE</h1>
            <p className="text-sm text-gray-400">Self-Healing Cloud Guardian</p>
          </div>
        </div>

        <div className="flex items-center gap-4">
          {/* Status Indicator */}
          {isIncidentActive && (
            <div className="flex items-center gap-2 px-3 py-2 bg-red-900/30 border border-red-600 rounded">
              <AlertTriangle className="w-4 h-4 text-red-400 animate-pulse" />
              <span className="text-sm text-red-400 font-semibold">
                Active: {incidentLabels[selectedIncident]}
              </span>
            </div>
          )}

          <div className="flex items-center gap-2">
            {isConnected ? (
              <>
                <Wifi className="w-5 h-5 text-green-400" />
                <span className="text-sm text-green-400">Connected</span>
              </>
            ) : (
              <>
                <WifiOff className="w-5 h-5 text-red-400" />
                <span className="text-sm text-red-400">Disconnected</span>
              </>
            )}
          </div>

          <div className="flex items-center gap-2">
            <select
              value={selectedIncident}
              onChange={(e) => setSelectedIncident(e.target.value)}
              disabled={isIncidentActive}
              className="px-4 py-2 bg-gray-700 border border-gray-600 rounded hover:bg-gray-600 transition-colors text-sm disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <option value="ddos">DDoS Attack</option>
              <option value="cpu_surge">CPU Surge</option>
              <option value="db_bottleneck">DB Bottleneck</option>
            </select>

            {!isIncidentActive ? (
              <button
                onClick={handleStart}
                className="flex items-center gap-2 px-4 py-2 bg-red-600 hover:bg-red-700 rounded transition-colors text-sm font-semibold"
              >
                <Play className="w-4 h-4" />
                Start Incident
              </button>
            ) : (
              <button
                onClick={handleStop}
                className="flex items-center gap-2 px-4 py-2 bg-yellow-600 hover:bg-yellow-700 rounded transition-colors text-sm font-semibold"
              >
                <Square className="w-4 h-4" />
                Stop Incident
              </button>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
