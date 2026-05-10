import React from 'react';
import { Wrench, CheckCircle, XCircle, Clock } from 'lucide-react';
import { RemediationAction } from '../types';
import { format } from 'date-fns';

interface Props {
  actions: RemediationAction[];
}

const RemediationLog: React.FC<Props> = ({ actions }) => {
  const getResultIcon = (result: string) => {
    switch (result) {
      case 'success': return <CheckCircle className="w-5 h-5 text-green-400" />;
      case 'failure': return <XCircle className="w-5 h-5 text-red-400" />;
      default: return <Clock className="w-5 h-5 text-yellow-400 animate-pulse" />;
    }
  };

  const getResultColor = (result: string) => {
    switch (result) {
      case 'success': return 'border-green-500 bg-green-900/20';
      case 'failure': return 'border-red-500 bg-red-900/20';
      default: return 'border-yellow-500 bg-yellow-900/20';
    }
  };

  return (
    <div className="bg-gray-800 rounded-lg shadow-xl p-4 h-full flex flex-col">
      <div className="flex items-center gap-2 mb-4">
        <Wrench className="w-5 h-5 text-orange-400" />
        <h2 className="text-xl font-bold">Remediation Action Log</h2>
      </div>

      <div className="flex-1 overflow-y-auto">
        {actions.length === 0 ? (
          <div className="text-center text-gray-500 py-8">
            <Wrench className="w-12 h-12 mx-auto mb-2 opacity-50" />
            <p>No remediation actions yet</p>
          </div>
        ) : (
          <div className="relative">
            <div className="absolute left-6 top-0 bottom-0 w-0.5 bg-gray-700" />
            <div className="space-y-4">
              {actions.map((action) => (
                <div key={action.id} className="relative pl-14">
                  <div className="absolute left-3 top-2 bg-gray-800 p-1 rounded-full border-2 border-gray-700">
                    {getResultIcon(action.result)}
                  </div>
                  <div className={`border-2 rounded-lg p-4 ${getResultColor(action.result)}`}>
                    <div className="flex items-start justify-between mb-2">
                      <h3 className="font-semibold text-lg">{action.action}</h3>
                      <span className="text-xs text-gray-400">
                        {format(new Date(action.timestamp), 'MMM dd, HH:mm:ss')}
                      </span>
                    </div>
                    
                    <div className="flex items-center gap-4 text-sm">
                      <div className="flex items-center gap-1">
                        <Clock className="w-4 h-4 text-gray-400" />
                        <span className="text-gray-400">Execution:</span>
                        <span className="text-blue-400 font-semibold">
                          {action.executionTime.toFixed(2)}s
                        </span>
                      </div>
                      <div className="flex items-center gap-1">
                        <span className="text-gray-400">Result:</span>
                        <span className={`font-semibold ${
                          action.result === 'success' ? 'text-green-400' :
                          action.result === 'failure' ? 'text-red-400' : 'text-yellow-400'
                        }`}>
                          {action.result.toUpperCase()}
                        </span>
                      </div>
                    </div>

                    {action.details && (
                      <div className="mt-3 bg-gray-900/50 p-3 rounded text-sm">
                        <p className="text-gray-300">{action.details}</p>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default RemediationLog;
