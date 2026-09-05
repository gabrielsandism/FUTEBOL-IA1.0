import { useEffect } from 'react';
import { useAppStore } from '@/store/appStore';
import { Header } from '@/components/Header';
import { Card, Badge, AlertBox } from '@/components/ui';
import { Trash2 } from 'lucide-react';

export default function Alerts() {
  const { alerts, fetchAlerts, dismissAlert } = useAppStore();

  useEffect(() => {
    fetchAlerts();
    const interval = setInterval(fetchAlerts, 10000);
    return () => clearInterval(interval);
  }, [fetchAlerts]);

  const activeAlerts = alerts.filter((a) => !a.is_dismissed);

  const getPriorityColor = (priority: number) => {
    if (priority >= 8) return 'danger';
    if (priority >= 6) return 'warning';
    return 'info';
  };

  return (
    <>
      <Header />
      <main className="min-h-screen bg-dark-900">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-dark-50 mb-2">Active Alerts</h1>
            <p className="text-dark-400">{activeAlerts.length} active alert{activeAlerts.length !== 1 ? 's' : ''}</p>
          </div>

          {activeAlerts.length === 0 ? (
            <AlertBox type="success">
              <div className="font-semibold">✓ No active alerts</div>
              <div className="text-sm mt-1">All systems operating normally</div>
            </AlertBox>
          ) : (
            <div className="space-y-4">
              {activeAlerts.map((alert) => (
                <Card
                  key={alert.id}
                  className={`border-l-4 ${
                    getPriorityColor(alert.priority) === 'danger'
                      ? 'border-l-danger'
                      : getPriorityColor(alert.priority) === 'warning'
                        ? 'border-l-warning'
                        : 'border-l-info'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-3">
                        <Badge variant={getPriorityColor(alert.priority) as any}>{alert.rule_code}</Badge>
                        <span className="font-bold text-dark-50 text-lg">{alert.title}</span>
                      </div>

                      <p className="text-dark-300 mb-4">{alert.message}</p>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <div className="text-xs text-dark-400 mb-1">Match</div>
                          <div className="text-dark-50 font-semibold">
                            {alert.home_team} vs {alert.away_team}
                          </div>
                          <div className="text-sm text-dark-400">{alert.league}</div>
                        </div>

                        <div>
                          <div className="text-xs text-dark-400 mb-1">Status</div>
                          <div className="flex items-center gap-2">
                            <Badge variant="info">{alert.minute}' • {alert.score}</Badge>
                            <span className="text-xs text-dark-400">
                              {new Date(alert.created_at).toLocaleTimeString()}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>

                    <button
                      onClick={() => dismissAlert(alert.id)}
                      className="ml-4 p-2 rounded-lg hover:bg-dark-700 text-dark-400 hover:text-danger transition-colors"
                      title="Dismiss alert"
                    >
                      <Trash2 size={20} />
                    </button>
                  </div>
                </Card>
              ))}
            </div>
          )}
        </div>
      </main>
    </>
  );
}
