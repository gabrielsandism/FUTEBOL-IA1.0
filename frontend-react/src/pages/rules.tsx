import { useEffect } from 'react';
import { useAppStore } from '@/store/appStore';
import { Header } from '@/components/Header';
import { Card, Badge, Button } from '@/components/ui';
import { Toggle } from 'lucide-react';

export default function Rules() {
  const { rules, fetchRules, toggleRule } = useAppStore();

  useEffect(() => {
    fetchRules();
  }, [fetchRules]);

  const CATEGORY_COLORS: Record<string, string> = {
    cards: 'warning',
    corners: 'info',
    goals: 'success',
    reversal: 'danger',
    two_legged: 'purple',
    general: 'info',
  };

  return (
    <>
      <Header />
      <main className="min-h-screen bg-dark-900">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-dark-50 mb-2">Rule Management</h1>
            <p className="text-dark-400">Configure and manage detection rules</p>
          </div>

          <div className="space-y-4">
            {rules.map((rule) => (
              <Card key={rule.rule_code}>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-3">
                      <span className="font-mono text-sm font-bold text-success">{rule.rule_code}</span>
                      <Badge variant={CATEGORY_COLORS[rule.category] as any}>
                        {rule.category}
                      </Badge>
                      <span className="text-xs text-dark-400">v{rule.version}</span>
                    </div>

                    <h3 className="text-lg font-bold text-dark-50 mb-2">{rule.name}</h3>
                    <p className="text-dark-400 text-sm mb-4">{rule.description}</p>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <div className="text-xs text-dark-400 mb-2">Priority</div>
                        <div className="flex items-center gap-1">
                          <div className="flex">
                            {Array.from({ length: 5 }).map((_, i) => (
                              <span
                                key={i}
                                className={`text-lg ${
                                  i < Math.round(rule.priority / 2) ? 'text-warning' : 'text-dark-600'
                                }`}
                              >
                                ★
                              </span>
                            ))}
                          </div>
                          <span className="text-xs text-dark-400">{rule.priority}/10</span>
                        </div>
                      </div>

                      {Object.keys(rule.parameters).length > 0 && (
                        <div>
                          <div className="text-xs text-dark-400 mb-2">Parameters</div>
                          <div className="space-y-1">
                            {Object.entries(rule.parameters)
                              .slice(0, 3)
                              .map(([key, value]) => (
                                <div key={key} className="text-xs text-dark-400">
                                  • <span className="font-mono">{key}</span>: {String(value)}
                                </div>
                              ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>

                  <button
                    onClick={() => toggleRule(rule.rule_code)}
                    className={`ml-4 px-4 py-2 rounded-lg font-semibold transition-colors ${
                      rule.is_active
                        ? 'bg-success text-dark-900 hover:bg-green-600'
                        : 'bg-dark-700 text-dark-400 hover:bg-dark-600'
                    }`}
                  >
                    {rule.is_active ? '✅ Active' : '❌ Inactive'}
                  </button>
                </div>
              </Card>
            ))}
          </div>
        </div>
      </main>
    </>
  );
}
