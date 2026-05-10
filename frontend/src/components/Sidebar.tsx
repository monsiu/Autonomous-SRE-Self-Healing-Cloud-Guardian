import React from 'react';
import { Terminal, Brain, Wrench, History, Activity, X, Database } from 'lucide-react';

interface Props {
  isOpen: boolean;
  onClose: () => void;
  activePanel: string;
  onPanelChange: (panel: string) => void;
}

const Sidebar: React.FC<Props> = ({ isOpen, onClose, activePanel, onPanelChange }) => {
  const panels = [
    { id: 'logs', name: 'Live Log Stream', icon: Terminal, color: 'text-green-400' },
    { id: 'health', name: 'System Health Score', icon: Activity, color: 'text-blue-400' },
    { id: 'agents', name: 'Agent Thinking', icon: Brain, color: 'text-purple-400' },
    { id: 'remediation', name: 'Remediation Log', icon: Wrench, color: 'text-orange-400' },
    { id: 'incidents', name: 'Incident Timeline', icon: History, color: 'text-indigo-400' },
    { id: 'stored-logs', name: 'Stored Logs', icon: Database, color: 'text-purple-400' },
  ];

  return (
    <>
      {/* Overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed top-0 left-0 h-full bg-gray-800 border-r border-gray-700 z-50 transform transition-transform duration-300 ease-in-out ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        } w-64`}
      >
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-gray-700">
            <h2 className="text-lg font-bold text-white">Dashboard Panels</h2>
            <button
              onClick={onClose}
              className="lg:hidden p-1 hover:bg-gray-700 rounded"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Panel List */}
          <nav className="flex-1 overflow-y-auto p-4">
            <div className="space-y-2">
              {panels.map((panel) => {
                const Icon = panel.icon;
                const isActive = activePanel === panel.id;
                
                return (
                  <button
                    key={panel.id}
                    onClick={() => {
                      onPanelChange(panel.id);
                      onClose();
                    }}
                    className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                      isActive
                        ? 'bg-gray-700 border-l-4 border-blue-500'
                        : 'hover:bg-gray-700/50'
                    }`}
                  >
                    <Icon className={`w-5 h-5 ${panel.color}`} />
                    <span className="text-sm font-medium text-gray-200">
                      {panel.name}
                    </span>
                  </button>
                );
              })}
            </div>
          </nav>

          {/* Footer */}
          <div className="p-4 border-t border-gray-700">
            <div className="text-xs text-gray-400 text-center">
              <p className="font-semibold">Autonomous SRE v1.0</p>
              <p className="mt-1">AMD Hackathon 2025</p>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
};

export default Sidebar;
