import { useEffect, useState } from 'react';
import { useAppStore } from '@/store/appStore';
import { Header } from '@/components/Header';
import { Card, Badge, Button } from '@/components/ui';
import { ChevronDown, ChevronUp } from 'lucide-react';

export default function Matches() {
  const { matches, fetchMatches } = useAppStore();
  const [expanded, setExpanded] = useState<number | null>(null);

  useEffect(() => {
    fetchMatches();
    const interval = setInterval(fetchMatches, 30000);
    return () => clearInterval(interval);
  }, [fetchMatches]);

  return (
    <>
      <Header />
      <main className="min-h-screen bg-dark-900">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-dark-50 mb-2">Live Matches</h1>
            <p className="text-dark-400">Real-time match data and statistics</p>
          </div>

          {matches.length === 0 ? (
            <Card>
              <div className="text-center py-12 text-dark-400">No live matches at the moment</div>
            </Card>
          ) : (
            <div className="space-y-4">
              {matches.map((match) => (
                <Card key={match.match_id} className="cursor-pointer hover:border-dark-600">
                  <button
                    onClick={() => setExpanded(expanded === match.match_id ? null : match.match_id)}
                    className="w-full text-left"
                  >
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <span className="font-bold text-dark-50">{match.home_team}</span>
                          <span className="text-lg font-bold text-dark-50">{match.home_score}</span>
                          <span className="text-dark-400">-</span>
                          <span className="text-lg font-bold text-dark-50">{match.away_score}</span>
                          <span className="font-bold text-dark-50">{match.away_team}</span>
                        </div>
                        <div className="text-sm text-dark-400">
                          {match.league} • {match.minute}' • {match.status}
                        </div>
                      </div>
                      <div className="flex flex-col items-end gap-2">
                        {match.active_alerts > 0 && (
                          <Badge variant="danger">🔴 {match.active_alerts} alerts</Badge>
                        )}
                        <button className="text-dark-400 hover:text-dark-50">
                          {expanded === match.match_id ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
                        </button>
                      </div>
                    </div>
                  </button>

                  {expanded === match.match_id && (
                    <div className="border-t border-dark-700 pt-4 mt-4">
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                        <div>
                          <div className="text-xs text-dark-400 mb-1">Home Team</div>
                          <div className="font-semibold text-dark-50">{match.home_team}</div>
                        </div>
                        <div>
                          <div className="text-xs text-dark-400 mb-1">Score</div>
                          <div className="text-2xl font-bold text-dark-50">{match.home_score}:{match.away_score}</div>
                        </div>
                        <div>
                          <div className="text-xs text-dark-400 mb-1">Away Team</div>
                          <div className="font-semibold text-dark-50">{match.away_team}</div>
                        </div>
                        <div>
                          <div className="text-xs text-dark-400 mb-1">Time</div>
                          <div className="text-lg font-bold text-success">{match.minute}'</div>
                        </div>
                      </div>

                      {match.alert_rules.length > 0 && (
                        <div className="bg-dark-900 border border-dark-700 rounded p-3">
                          <div className="text-xs text-dark-400 mb-2">Active Rules</div>
                          <div className="flex flex-wrap gap-2">
                            {match.alert_rules.map((rule) => (
                              <Badge key={rule} variant="warning">
                                {rule}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </Card>
              ))}
            </div>
          )}
        </div>
      </main>
    </>
  );
}
