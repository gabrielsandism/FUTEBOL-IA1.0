import { useEffect } from 'react';
import { useAppStore } from '@/store/appStore';
import { Header } from '@/components/Header';
import { Card, Metric, Button, Badge, AlertBox } from '@/components/ui';
import { RefreshCw, AlertCircle, Zap } from 'lucide-react';

export default function Dashboard() {
  const { matches, alerts, stats, loading, fetchMatches, fetchAlerts, fetchStats, dismissAlert } = useAppStore();

  useEffect(() => {
    fetchMatches();
    fetchAlerts();
    fetchStats();

    const interval = setInterval(() => {
      fetchMatches();
      fetchAlerts();
      fetchStats();
    }, 30000);

    return () => clearInterval(interval);
  }, [fetchMatches, fetchAlerts, fetchStats]);

  const activeAlerts = alerts.filter((a) => !a.is_dismissed);

  return (
    <>
      <Header />
      <main className="min-h-screen bg-dark-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Header Section */}
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-3xl font-bold text-dark-50">Dashboard</h1>
              <p className="text-dark-400 mt-1">Real-time match monitoring and analysis</p>
            </div>
            <Button
              onClick={() => {
                fetchMatches();
                fetchAlerts();
                fetchStats();
              }}
              variant="secondary"
              className="flex items-center gap-2"
            >
              <RefreshCw size={18} />
              Refresh
            </Button>
          </div>

          {/* Metrics Row */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <Metric label="🎮 Live Matches" value={matches.length} />
            <Metric label="🔔 Active Alerts" value={activeAlerts.length} />
            <Metric label="📊 Evaluations" value={stats?.total_evaluations || 0} />
            <Metric label="⚙️ Active Rules" value={stats?.active_rules || 0} />
          </div>

          {/* Live Matches Section */}
          <Card className="mb-8">
            <div className="flex items-center gap-2 mb-6">
              <div className="live-dot"></div>
              <h2 className="text-xl font-bold text-dark-50">Live Matches</h2>
            </div>

            {loading ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-success mx-auto"></div>
              </div>
            ) : matches.length === 0 ? (
              <div className="text-center py-8 text-dark-400">No live matches at the moment</div>
            ) : (
              <div className="space-y-4">
                {matches.map((match) => (
                  <div
                    key={match.match_id}
                    className="bg-dark-900 border border-dark-700 rounded-lg p-4 hover:border-dark-600 transition-colors"
                  >
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                      <div>
                        <div className="text-sm text-dark-400 mb-1">Home</div>
                        <div className="font-semibold text-dark-50">{match.home_team}</div>
                      </div>

                      <div className="flex flex-col items-center justify-center">
                        <div className="text-sm text-dark-400 mb-1">Score</div>
                        <div className="text-3xl font-bold text-dark-50">{match.home_score}</div>
                        <div className="text-xs text-dark-400 mt-1">-</div>
                        <div className="text-3xl font-bold text-dark-50">{match.away_score}</div>
                      </div>

                      <div>
                        <div className="text-sm text-dark-400 mb-1">Away</div>
                        <div className="font-semibold text-dark-50">{match.away_team}</div>
                      </div>

                      <div className="flex flex-col justify-center">
                        <div className="text-sm text-dark-400 mb-2">{match.league}</div>
                        <Badge variant="info">{match.minute}' • {match.status}</Badge>
                        {match.active_alerts > 0 && (
                          <Badge variant="danger" className="mt-2">
                            🔴 {match.active_alerts} alert{match.active_alerts > 1 ? 's' : ''}
                          </Badge>
                        )}
                        {match.alert_rules.length > 0 && (
                          <div className="mt-2 flex flex-wrap gap-1">
                            {match.alert_rules.map((rule) => (
                              <Badge key={rule} variant="warning">
                                {rule}
                              </Badge>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </Card>

          {/* Active Alerts Section */}
          <Card>
            <div className="flex items-center gap-2 mb-6">
              <AlertCircle size={24} className="text-warning" />
              <h2 className="text-xl font-bold text-dark-50">Active Alerts</h2>
            </div>

            {activeAlerts.length === 0 ? (
              <AlertBox type="success">
                <div className="font-semibold">✓ No active alerts</div>
              </AlertBox>
            ) : (
              <div className="space-y-4">
                {activeAlerts.slice(0, 10).map((alert) => (
                  <div
                    key={alert.id}
                    className={`bg-dark-900 border-l-4 rounded-lg p-4 ${
                      alert.priority >= 8
                        ? 'border-danger'
                        : alert.priority >= 6
                          ? 'border-warning'
                          : 'border-info'
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <Badge variant={alert.priority >= 8 ? 'danger' : alert.priority >= 6 ? 'warning' : 'info'}>
                            {alert.rule_code}
                          </Badge>
                          <span className="font-semibold text-dark-50">{alert.title}</span>
                        </div>
                        <p className="text-dark-400 text-sm mb-2">{alert.message.substring(0, 200)}...</p>
                        <div className="text-xs text-dark-500">
                          {alert.home_team} vs {alert.away_team} • {alert.league} • {alert.minute}' • {alert.score}
                        </div>
                      </div>
                      <button
                        onClick={() => dismissAlert(alert.id)}
                        className="text-dark-400 hover:text-danger transition-colors ml-4"
                      >
                        ✕
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </Card>
        </div>
      </main>
    </>
  );
}
