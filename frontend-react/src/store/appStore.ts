import { create } from 'zustand';

export interface Match {
  match_id: number;
  home_team: string;
  away_team: string;
  league: string;
  home_score: number;
  away_score: number;
  minute: number;
  status: string;
  active_alerts: number;
  alert_rules: string[];
}

export interface Alert {
  id: number;
  rule_code: string;
  rule_name: string;
  match_id: number;
  priority: number;
  title: string;
  message: string;
  home_team: string;
  away_team: string;
  league: string;
  minute: number;
  score: string;
  is_read: boolean;
  is_dismissed: boolean;
  created_at: string;
  expires_at: string;
}

export interface Rule {
  rule_code: string;
  name: string;
  category: string;
  description: string;
  priority: number;
  version: string;
  is_active: boolean;
  parameters: Record<string, any>;
}

interface AppState {
  matches: Match[];
  alerts: Alert[];
  rules: Rule[];
  stats: Record<string, any>;
  loading: boolean;
  error: string | null;
  
  setMatches: (matches: Match[]) => void;
  setAlerts: (alerts: Alert[]) => void;
  setRules: (rules: Rule[]) => void;
  setStats: (stats: Record<string, any>) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  
  fetchMatches: () => Promise<void>;
  fetchAlerts: () => Promise<void>;
  fetchRules: () => Promise<void>;
  fetchStats: () => Promise<void>;
  
  dismissAlert: (alertId: number) => Promise<void>;
  toggleRule: (ruleCode: string) => Promise<void>;
}

export const useAppStore = create<AppState>((set) => ({
  matches: [],
  alerts: [],
  rules: [],
  stats: {},
  loading: false,
  error: null,

  setMatches: (matches) => set({ matches }),
  setAlerts: (alerts) => set({ alerts }),
  setRules: (rules) => set({ rules }),
  setStats: (stats) => set({ stats }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),

  fetchMatches: async () => {
    set({ loading: true });
    try {
      const res = await fetch('/api/matches/live');
      const data = await res.json();
      set({ matches: data.matches || [], error: null });
    } catch (error) {
      set({ error: (error as Error).message });
    } finally {
      set({ loading: false });
    }
  },

  fetchAlerts: async () => {
    try {
      const res = await fetch('/api/alerts/');
      const data = await res.json();
      set({ alerts: data.alerts || [] });
    } catch (error) {
      set({ error: (error as Error).message });
    }
  },

  fetchRules: async () => {
    try {
      const res = await fetch('/api/rules/');
      const data = await res.json();
      set({ rules: data.rules || [] });
    } catch (error) {
      set({ error: (error as Error).message });
    }
  },

  fetchStats: async () => {
    try {
      const res = await fetch('/api/stats');
      const data = await res.json();
      set({ stats: data });
    } catch (error) {
      set({ error: (error as Error).message });
    }
  },

  dismissAlert: async (alertId) => {
    try {
      await fetch(`/api/alerts/${alertId}/dismiss`, { method: 'POST' });
      set((state) => ({
        alerts: state.alerts.map((a) =>
          a.id === alertId ? { ...a, is_dismissed: true } : a
        ),
      }));
    } catch (error) {
      set({ error: (error as Error).message });
    }
  },

  toggleRule: async (ruleCode) => {
    try {
      const rule = useAppStore.getState().rules.find((r) => r.rule_code === ruleCode);
      if (!rule) return;
      
      await fetch(`/api/rules/${ruleCode}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ is_active: !rule.is_active }),
      });
      
      await useAppStore.getState().fetchRules();
    } catch (error) {
      set({ error: (error as Error).message });
    }
  },
}));
