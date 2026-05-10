import React from 'react';
import { Activity, TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { SystemHealth } from '../types';

interface Props {
  health: SystemHealth;
  history: Array<{ timestamp: string; score: number }>;
}

const SystemHealthScore: React.FC<Props> = ({ health, history }) => {
  const getTrendIcon = () => {
    switch (health.trend) {
      case 'improving': return <TrendingUp className="w-5 h-5 text-green-400" />;
      case 'degrading': return <TrendingDown className="w-5 h-5 text-red-400" />;
      default: return <Minus className="w-5 h-5 text-yellow-400" />;
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-400';
    if (score >= 60) return 'text-yellow-400';
    if (score >= 40) return 'text-orange-400';
    return 'text-red-400';
  };

  const getMetricColor = (value: number, isInverted = false) => {
    const threshold = isInverted ? 
      (value > 70 ? 'text-red-400' : value > 50 ? 'text-yellow-400' : 'text-green-400') :
      (value > 70 ? 'text-green-400' : value > 50 ? 'text-yellow-400' : 'text-red-400');
    return threshold;
  };

  return (
    <div className="bg-gray-800 rounded-lg shadow-xl p-4 h-full flex flex-col">
      <div className="flex items-center gap-2 mb-4">
        <Activity className="w-5 h-5 text-green-400" />
        <h2 className="text-xl font-bold">System Health Score</h2>
      </div>

      {/* Top Section - Current Health and Prediction */}
      <div className="flex gap-4 mb-4">
        <div className="flex-1 bg-gray-900/50 p-4 rounded-lg text-center">
          <p className="text-sm text-gray-400 mb-2">Current Health</p>
          <div className="flex items-center justify-center gap-2">
            <span className={`text-5xl font-bold ${getScoreColor(health.score)}`}>
              {health.score}
            </span>
            <span className="text-2xl text-gray-500">/100</span>
          </div>
          <div className="flex items-center justify-center gap-2 mt-2">
            {getTrendIcon()}
            <span className="text-sm text-gray-400 capitalize">{health.trend}</span>
          </div>
        </div>

        <div className="flex-1 bg-gray-900/50 p-4 rounded-lg">
          <p className="text-sm text-gray-400 mb-3">Predictive Analysis</p>
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <span className="text-xs text-gray-400">Next Hour Score:</span>
              <span className={`text-lg font-bold ${getScoreColor(health.prediction.nextHourScore)}`}>
                {health.prediction.nextHourScore}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-xs text-gray-400">Confidence:</span>
              <span className="text-lg font-bold text-blue-400">
                {(health.prediction.confidence * 100).toFixed(0)}%
              </span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-2 mt-2">
              <div
                className="bg-blue-500 h-2 rounded-full transition-all"
                style={{ width: `${health.prediction.confidence * 100}%` }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-4 gap-3 mb-4">
        <div className="bg-gray-900/50 p-3 rounded text-center">
          <p className="text-xs text-gray-400 mb-1">CPU</p>
          <p className={`text-xl font-bold ${getMetricColor(health.metrics.cpu, true)}`}>
            {health.metrics.cpu}%
          </p>
        </div>
        <div className="bg-gray-900/50 p-3 rounded text-center">
          <p className="text-xs text-gray-400 mb-1">Memory</p>
          <p className={`text-xl font-bold ${getMetricColor(health.metrics.memory, true)}`}>
            {health.metrics.memory}%
          </p>
        </div>
        <div className="bg-gray-900/50 p-3 rounded text-center">
          <p className="text-xs text-gray-400 mb-1">Error Rate</p>
          <p className={`text-xl font-bold ${getMetricColor(100 - health.metrics.errorRate)}`}>
            {health.metrics.errorRate.toFixed(1)}%
          </p>
        </div>
        <div className="bg-gray-900/50 p-3 rounded text-center">
          <p className="text-xs text-gray-400 mb-1">Response</p>
          <p className={`text-xl font-bold ${getMetricColor(health.metrics.responseTime > 500 ? 30 : 80)}`}>
            {health.metrics.responseTime}ms
          </p>
        </div>
      </div>

      {/* Chart Section */}
      <div className="flex-1 bg-gray-900/50 p-3 rounded min-h-0">
        <p className="text-sm text-gray-400 mb-2">Health Trend (Last Hour)</p>
        <div className="h-[calc(100%-2rem)]">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={history}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis 
                dataKey="timestamp" 
                stroke="#9CA3AF"
                tick={{ fontSize: 12 }}
              />
              <YAxis 
                stroke="#9CA3AF"
                domain={[0, 100]}
                tick={{ fontSize: 12 }}
              />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#1F2937', 
                  border: '1px solid #374151',
                  borderRadius: '0.5rem'
                }}
              />
              <Line 
                type="monotone" 
                dataKey="score" 
                stroke="#10B981" 
                strokeWidth={2}
                dot={{ fill: '#10B981', r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

export default SystemHealthScore;
