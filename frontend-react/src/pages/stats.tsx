import { useEffect } from 'react';
import { useAppStore } from '@/store/appStore';
import { Header } from '@/components/Header';
import { Card, Metric, AlertBox } from '@/components/ui';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export default function Stats() {
  const { stats, fetchStats, rules, fetchRules } = useAppStore();

  useEffect(() => {
    fetchStats();
    fetchRules();
    const interval = setInterval(() => {
      fetchStats();
      fetchRules();
    }, 60000);
    return () => clearInterval(interval);
  }, [fetchStats, fetchRules]);

  const chartData = rules.map((rule) => ({
    name: rule.rule_code,
    active: rule.is_active ? 1 : 0,
    priority: rule.priority,
  }));

  return (
    <>
      <Header />
      <main className="min-h-screen bg-dark-900">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-dark-50 mb-2">Statistics</h1>
            <p className="text-dark-400">System performance and metrics</p>
          </div>

          {/* Top Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <Metric label="Provider" value={stats.provider || '-'} />
            <Metric label="Total Evaluations" value={stats.total_evaluations || 0} />
            <Metric label="Alerts Generated" value={stats.total_alerts_generated || 0} />
            <Metric label="Live Matches" value={stats.live_matches || 0} />
          </div>

          {/* Configuration */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
            <Card>
              <h3 className="text-lg font-bold text-dark-50 mb-4">Configuration</h3>
              <div className="space-y-3">
                <div>
                  <div className="text-xs text-dark-400">Interval</div>
                  <div className="text-dark-50 font-semibold">{stats.interval_seconds}s</div>
                </div>
                <div>
                  <div className="text-xs text-dark-400">Active Alerts</div>
                  <div className="text-dark-50 font-semibold">{stats.active_alerts || 0}</div>
                </div>
                <div>
                  <div className="text-xs text-dark-400">Active Rules</div>
                  <div className="text-dark-50 font-semibold">{stats.active_rules || 0}</div>
                </div>
              </div>
            </Card>

            <Card>
              <h3 className="text-lg font-bold text-dark-50 mb-4">Last Update</h3>
              {stats.last_update ? (
                <div>
                  <div className="text-xs text-dark-400 mb-2">Timestamp</div>
                  <div className="text-dark-50 font-semibold">
                    {new Date(stats.last_update).toLocaleString()}
                  </div>
                  <div className="text-xs text-dark-400 mt-3">Status</div>
                  <div className="text-success font-semibold">✓ System Online</div>
                </div>
              ) : (
                <AlertBox type="warning">Awaiting first update...</AlertBox>
              )}
            </Card>
          </div>

          {/* Rules Overview Chart */}
          {rules.length > 0 && (
            <Card>
              <h3 className="text-lg font-bold text-dark-50 mb-6">Rules Overview</h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#30363d" />
                  <XAxis dataKey="name" stroke="#8b949e" />
                  <YAxis stroke="#8b949e" />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#161b22',
                      border: '1px solid #30363d',
                      borderRadius: '4px',
                      color: '#e6edf3',
                    }}
                  />
                  <Bar dataKey="priority" fill="#3fb950" name="Priority" />
                </BarChart>
              </ResponsiveContainer>
            </Card>
          )}

          {/* Rules Table */}
          <Card className="mt-8">
            <h3 className="text-lg font-bold text-dark-50 mb-4">Rules Status</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-dark-700">
                    <th className="text-left py-3 px-4 text-dark-400 font-semibold text-xs">Code</th>
                    <th className="text-left py-3 px-4 text-dark-400 font-semibold text-xs">Name</th>
                    <th className="text-left py-3 px-4 text-dark-400 font-semibold text-xs">Category</th>
                    <th className="text-left py-3 px-4 text-dark-400 font-semibold text-xs">Priority</th>
                    <th className="text-left py-3 px-4 text-dark-400 font-semibold text-xs">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {rules.map((rule) => (
                    <tr key={rule.rule_code} className="border-b border-dark-700 hover:bg-dark-800">
                      <td className="py-3 px-4 font-mono text-success text-xs">{rule.rule_code}</td>
                      <td className="py-3 px-4 text-dark-50">{rule.name}</td>
                      <td className="py-3 px-4 text-dark-400 text-xs uppercase">{rule.category}</td>
                      <td className="py-3 px-4">
                        <div className="flex">
                          {Array.from({ length: 5 }).map((_, i) => (
                            <span
                              key={i}
                              className={i < Math.round(rule.priority / 2) ? 'text-warning' : 'text-dark-600'}
                            >
                              ★
                            </span>
                          ))}
                        </div>
                      </td>
                      <td className="py-3 px-4">
                        <span
                          className={`inline-block px-3 py-1 rounded text-xs font-semibold ${
                            rule.is_active
                              ? 'bg-green-900/30 text-success'
                              : 'bg-dark-700 text-dark-400'
                          }`}
                        >
                          {rule.is_active ? '✓ Active' : '○ Inactive'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        </div>
      </main>
    </>
  );
}
