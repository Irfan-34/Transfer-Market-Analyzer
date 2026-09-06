import React, { useState, useEffect } from 'react';
import { 
  Activity, TrendingUp, Users, ShieldAlert, Cpu, Search, RefreshCw, 
  DollarSign, Sparkles, Filter, ExternalLink, ArrowRightLeft, Radio, BarChart3
} from 'lucide-react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, AreaChart, Area } from 'recharts';

const API_BASE = 'http://localhost:8000';

export default function App() {
  const [activeTab, setActiveTab] = useState('overview');
  const [healthStatus, setHealthStatus] = useState(null);
  const [marketSummary, setMarketSummary] = useState(null);
  const [spendingSeason, setSpendingSeason] = useState([]);
  const [latestTransfers, setLatestTransfers] = useState([]);
  const [topPredictions, setTopPredictions] = useState([]);
  const [rumours, setRumours] = useState([]);
  const [sources, setSources] = useState([]);
  const [players, setPlayers] = useState([]);
  const [clubs, setClubs] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedPlayer, setSelectedPlayer] = useState(null);
  const [selectedClub, setSelectedClub] = useState(null);

  // Prediction Calculator State
  const [calcPlayer, setCalcPlayer] = useState('Florian Wirtz');
  const [calcValuation, setCalcValuation] = useState(130000000);
  const [calcPosition, setCalcPosition] = useState('Attack');
  const [calcBuyingClub, setCalcBuyingClub] = useState('Real Madrid');
  const [calcResult, setCalcResult] = useState(null);
  const [isCalculating, setIsCalculating] = useState(false);

  useEffect(() => {
    fetchHealth();
    fetchMarketSummary();
    fetchLatestTransfers();
    fetchTopPredictions();
    fetchRumours();
    fetchSources();
    fetchPlayers();
    fetchClubs();
  }, []);

  const fetchHealth = async () => {
    try {
      const res = await fetch(`${API_BASE}/health`);
      if (res.ok) setHealthStatus(await res.json());
    } catch (e) {
      setHealthStatus({ status: 'OFFLINE', database_status: 'DISCONNECTED' });
    }
  };

  const fetchMarketSummary = async () => {
    try {
      const res = await fetch(`${API_BASE}/market/summary`);
      if (res.ok) setMarketSummary(await res.json());

      const resSpending = await fetch(`${API_BASE}/market/spending?limit=10`);
      if (resSpending.ok) setSpendingSeason(await resSpending.json());
    } catch (e) {
      console.error(e);
    }
  };

  const fetchLatestTransfers = async () => {
    try {
      const res = await fetch(`${API_BASE}/transfers/latest?limit=12`);
      if (res.ok) setLatestTransfers(await res.json());
    } catch (e) {
      console.error(e);
    }
  };

  const fetchTopPredictions = async () => {
    try {
      const res = await fetch(`${API_BASE}/predictions/top`);
      if (res.ok) setTopPredictions(await res.json());
    } catch (e) {
      console.error(e);
    }
  };

  const fetchRumours = async () => {
    try {
      const res = await fetch(`${API_BASE}/rumours?limit=15`);
      if (res.ok) setRumours(await res.json());
    } catch (e) {
      console.error(e);
    }
  };

  const fetchSources = async () => {
    try {
      const res = await fetch(`${API_BASE}/sources/reliability`);
      if (res.ok) setSources(await res.json());
    } catch (e) {
      console.error(e);
    }
  };

  const fetchPlayers = async (query = '') => {
    try {
      const res = await fetch(`${API_BASE}/players?search=${encodeURIComponent(query)}&limit=15`);
      if (res.ok) {
        const data = await res.json();
        setPlayers(data.players || []);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const fetchClubs = async (query = '') => {
    try {
      const res = await fetch(`${API_BASE}/clubs?search=${encodeURIComponent(query)}&limit=15`);
      if (res.ok) {
        const data = await res.json();
        setClubs(data.clubs || []);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const runPredictionCalculator = async () => {
    setIsCalculating(true);
    try {
      const res = await fetch(`${API_BASE}/predictions/transfer`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          player_name: calcPlayer,
          player_market_value_eur: parseFloat(calcValuation),
          position: calcPosition,
          buying_club_name: calcBuyingClub
        })
      });
      if (res.ok) {
        const data = await res.json();
        setCalcResult(data);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setIsCalculating(false);
    }
  };

  const formatEuro = (val) => {
    if (!val) return '€0';
    if (val >= 1e9) return `€${(val / 1e9).toFixed(2)}B`;
    if (val >= 1e6) return `€${(val / 1e6).toFixed(1)}M`;
    if (val >= 1e3) return `€${(val / 1e3).toFixed(0)}K`;
    return `€${val}`;
  };

  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      {/* Sidebar Navigation */}
      <aside style={{ width: '260px', background: 'rgba(15, 23, 42, 0.95)', borderRight: '1px solid var(--border-color)', padding: '24px 16px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
        <div style={{ padding: '0 12px 24px', display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{ width: '40px', height: '40px', borderRadius: '12px', background: 'linear-gradient(135deg, #06b6d4, #3b82f6)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '20px' }}>
            ⚽
          </div>
          <div>
            <h1 style={{ fontSize: '1.1rem', fontWeight: '800', letterSpacing: '-0.02em', background: 'linear-gradient(to right, #f8fafc, #94a3b8)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
              TM ANALYZER
            </h1>
            <span style={{ fontSize: '0.7rem', color: 'var(--accent-cyan)', fontWeight: '600', letterSpacing: '0.05em' }}>PRO INTELLIGENCE</span>
          </div>
        </div>

        <nav style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
          {[
            { id: 'overview', label: 'Overview', icon: Activity },
            { id: 'transfers', label: 'Live Transfers', icon: ArrowRightLeft },
            { id: 'rumours', label: 'Rumour Tracker', icon: Radio },
            { id: 'predictions', label: 'ML Predictions', icon: Sparkles },
            { id: 'players', label: 'Player Database', icon: Users },
            { id: 'clubs', label: 'Club Profiler', icon: TrendingUp },
            { id: 'market', label: 'Market Analytics', icon: BarChart3 },
            { id: 'system', label: 'System & Models', icon: Cpu }
          ].map(tab => {
            const Icon = tab.icon;
            const active = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px',
                  padding: '12px 16px',
                  borderRadius: '12px',
                  border: 'none',
                  background: active ? 'rgba(6, 182, 212, 0.15)' : 'transparent',
                  color: active ? '#38bdf8' : 'var(--text-muted)',
                  fontWeight: active ? '700' : '500',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease',
                  textAlign: 'left'
                }}
              >
                <Icon size={18} color={active ? '#38bdf8' : '#94a3b8'} />
                {tab.label}
              </button>
            );
          })}
        </nav>
      </aside>

      {/* Main Content Area */}
      <main style={{ flex: 1, padding: '32px 40px', overflowY: 'auto' }}>
        {/* Top Header Bar */}
        <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '32px' }}>
          <div>
            <h2 style={{ fontSize: '1.75rem', fontWeight: '800', color: '#f8fafc' }}>
              {activeTab.charAt(0).toUpperCase() + activeTab.slice(1)} Dashboard
            </h2>
            <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>
              Historical transfer analytics & real-time probabilistic ML predictions
            </p>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <div className="glass-panel" style={{ padding: '8px 16px', display: 'flex', alignItems: 'center', gap: '10px' }}>
              <div style={{ width: '10px', height: '10px', borderRadius: '50%', background: healthStatus?.status === 'ONLINE' ? '#10b981' : '#f43f5e', boxShadow: healthStatus?.status === 'ONLINE' ? '0 0 10px #10b981' : 'none' }} />
              <span style={{ fontSize: '0.8rem', fontWeight: '600' }}>
                API: {healthStatus?.status || 'CONNECTING...'}
              </span>
            </div>

            <button onClick={fetchMarketSummary} style={{ background: 'rgba(255,255,255,0.05)', border: '1px solid var(--border-color)', color: '#fff', width: '40px', height: '40px', borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer' }}>
              <RefreshCw size={16} />
            </button>
          </div>
        </header>

        {/* OVERVIEW TAB */}
        {activeTab === 'overview' && (
          <div>
            {/* KPI Cards */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '20px', marginBottom: '32px' }}>
              <div className="glass-panel" style={{ padding: '24px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', color: 'var(--text-muted)', marginBottom: '8px' }}>
                  <span style={{ fontSize: '0.85rem', fontWeight: '600' }}>Total Transfers</span>
                  <ArrowRightLeft size={20} color="#06b6d4" />
                </div>
                <div style={{ fontSize: '1.8rem', fontWeight: '800' }}>
                  {marketSummary ? marketSummary.total_transfers.toLocaleString() : '175,165'}
                </div>
                <span style={{ fontSize: '0.75rem', color: 'var(--accent-emerald)' }}>Historical Database</span>
              </div>

              <div className="glass-panel" style={{ padding: '24px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', color: 'var(--text-muted)', marginBottom: '8px' }}>
                  <span style={{ fontSize: '0.85rem', fontWeight: '600' }}>Total Market Volume</span>
                  <DollarSign size={20} color="#10b981" />
                </div>
                <div style={{ fontSize: '1.8rem', fontWeight: '800' }}>
                  {marketSummary ? formatEuro(marketSummary.total_spending_eur) : '€94.5B'}
                </div>
                <span style={{ fontSize: '0.75rem', color: 'var(--accent-cyan)' }}>Recorded Spending</span>
              </div>

              <div className="glass-panel" style={{ padding: '24px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', color: 'var(--text-muted)', marginBottom: '8px' }}>
                  <span style={{ fontSize: '0.85rem', fontWeight: '600' }}>Average Transfer Fee</span>
                  <TrendingUp size={20} color="#f59e0b" />
                </div>
                <div style={{ fontSize: '1.8rem', fontWeight: '800' }}>
                  {marketSummary ? formatEuro(marketSummary.avg_transfer_fee_eur) : '€2.1M'}
                </div>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Median: {marketSummary ? formatEuro(marketSummary.median_transfer_fee_eur) : '€400K'}</span>
              </div>

              <div className="glass-panel" style={{ padding: '24px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', color: 'var(--text-muted)', marginBottom: '8px' }}>
                  <span style={{ fontSize: '0.85rem', fontWeight: '600' }}>Tracked Players</span>
                  <Users size={20} color="#8b5cf6" />
                </div>
                <div style={{ fontSize: '1.8rem', fontWeight: '800' }}>
                  {marketSummary ? marketSummary.total_players_recorded.toLocaleString() : '50,149'}
                </div>
                <span style={{ fontSize: '0.75rem', color: 'var(--accent-purple)' }}>Across 796 Clubs</span>
              </div>
            </div>

            {/* Charts Grid */}
            <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '24px', marginBottom: '32px' }}>
              <div className="glass-panel" style={{ padding: '24px' }}>
                <h3 style={{ fontSize: '1.1rem', fontWeight: '700', marginBottom: '16px' }}>Annual Transfer Spending Trend</h3>
                <div style={{ height: '300px' }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={spendingSeason}>
                      <defs>
                        <linearGradient id="colorSpend" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.4}/>
                          <stop offset="95%" stopColor="#06b6d4" stopOpacity={0}/>
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                      <XAxis dataKey="season" stroke="#94a3b8" />
                      <YAxis stroke="#94a3b8" tickFormatter={(v) => `€${(v/1e9).toFixed(1)}B`} />
                      <Tooltip formatter={(value) => [formatEuro(value), 'Spending']} contentStyle={{ background: '#0f172a', border: '1px solid #1e293b' }} />
                      <Area type="monotone" dataKey="total_spending_eur" stroke="#06b6d4" fillOpacity={1} fill="url(#colorSpend)" />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* High Probability Predictions */}
              <div className="glass-panel" style={{ padding: '24px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
                  <Sparkles size={18} color="#06b6d4" />
                  <h3 style={{ fontSize: '1.1rem', fontWeight: '700' }}>Top Predicted Transfers</h3>
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  {topPredictions.map((pred, i) => (
                    <div key={i} style={{ background: 'rgba(255,255,255,0.03)', padding: '12px', borderRadius: '12px', border: '1px solid var(--border-color)' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontWeight: '700', fontSize: '0.9rem' }}>
                        <span>{pred.player_name}</span>
                        <span style={{ color: '#38bdf8' }}>{(pred.probability * 100).toFixed(0)}% Prob</span>
                      </div>
                      <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                        {pred.current_club} ➔ <strong style={{ color: '#fff' }}>{pred.buying_club}</strong>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* LIVE TRANSFERS TAB */}
        {activeTab === 'transfers' && (
          <div className="glass-panel" style={{ padding: '24px' }}>
            <h3 style={{ fontSize: '1.2rem', fontWeight: '700', marginBottom: '16px' }}>Completed Transfers Feed</h3>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                  <th style={{ padding: '12px' }}>Player</th>
                  <th style={{ padding: '12px' }}>From Club</th>
                  <th style={{ padding: '12px' }}>To Club</th>
                  <th style={{ padding: '12px' }}>Season</th>
                  <th style={{ padding: '12px' }}>Transfer Fee</th>
                </tr>
              </thead>
              <tbody>
                {latestTransfers.map((t, idx) => (
                  <tr key={idx} style={{ borderBottom: '1px solid rgba(255,255,255,0.03)', fontSize: '0.9rem' }}>
                    <td style={{ padding: '14px 12px', fontWeight: '700' }}>{t.player_name}</td>
                    <td style={{ padding: '14px 12px', color: 'var(--text-muted)' }}>{t.from_club_name || 'Free Agent'}</td>
                    <td style={{ padding: '14px 12px', color: '#38bdf8', fontWeight: '600' }}>{t.to_club_name}</td>
                    <td style={{ padding: '14px 12px', color: 'var(--text-muted)' }}>{t.transfer_season}</td>
                    <td style={{ padding: '14px 12px', fontWeight: '700', color: t.fee_eur > 0 ? '#10b981' : '#94a3b8' }}>
                      {t.fee_eur > 0 ? formatEuro(t.fee_eur) : 'Free Transfer'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* RUMOUR TRACKER TAB */}
        {activeTab === 'rumours' && (
          <div>
            <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '24px' }}>
              <div className="glass-panel" style={{ padding: '24px' }}>
                <h3 style={{ fontSize: '1.2rem', fontWeight: '700', marginBottom: '16px' }}>Ingested Rumours & Media Links</h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  {rumours.map((r, i) => (
                    <div key={i} style={{ background: 'rgba(255,255,255,0.03)', padding: '16px', borderRadius: '12px', border: '1px solid var(--border-color)' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                        <span className={`badge badge-${r.status.toLowerCase()}`}>{r.status}</span>
                        <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Source: {r.source_name}</span>
                      </div>
                      <div style={{ fontSize: '1rem', fontWeight: '700', color: '#f8fafc' }}>
                        {r.player_name} linked with <span style={{ color: '#38bdf8' }}>{r.to_club_name}</span>
                      </div>
                      <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '6px' }}>
                        Confidence Score: {(r.confidence_score * 100).toFixed(0)}%
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Source Reliability Table */}
              <div className="glass-panel" style={{ padding: '24px' }}>
                <h3 style={{ fontSize: '1.1rem', fontWeight: '700', marginBottom: '16px' }}>Media Reliability Index</h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  {sources.map((s, i) => (
                    <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px 0', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                      <div>
                        <div style={{ fontWeight: '700', fontSize: '0.9rem' }}>{s.source_name}</div>
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{s.confirmed_outcomes}/{s.rumours_reported} confirmed</div>
                      </div>
                      <div style={{ fontWeight: '800', color: s.reliability_score >= 0.75 ? '#10b981' : '#f59e0b' }}>
                        {(s.reliability_score * 100).toFixed(0)}%
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ML PREDICTIONS TAB & CALCULATOR */}
        {activeTab === 'predictions' && (
          <div>
            <div className="glass-panel" style={{ padding: '28px', marginBottom: '32px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '20px' }}>
                <Sparkles size={22} color="#06b6d4" />
                <h3 style={{ fontSize: '1.25rem', fontWeight: '800' }}>Predict Transfer Probability & Expected Fee</h3>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', marginBottom: '20px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '6px' }}>Player Name</label>
                  <input value={calcPlayer} onChange={e => setCalcPlayer(e.target.value)} style={{ width: '100%', padding: '10px 14px', borderRadius: '8px', background: 'rgba(255,255,255,0.05)', border: '1px solid var(--border-color)', color: '#fff' }} />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '6px' }}>Market Value (€)</label>
                  <input type="number" value={calcValuation} onChange={e => setCalcValuation(e.target.value)} style={{ width: '100%', padding: '10px 14px', borderRadius: '8px', background: 'rgba(255,255,255,0.05)', border: '1px solid var(--border-color)', color: '#fff' }} />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '6px' }}>Target Buying Club</label>
                  <input value={calcBuyingClub} onChange={e => setCalcBuyingClub(e.target.value)} style={{ width: '100%', padding: '10px 14px', borderRadius: '8px', background: 'rgba(255,255,255,0.05)', border: '1px solid var(--border-color)', color: '#fff' }} />
                </div>
              </div>

              <button onClick={runPredictionCalculator} style={{ padding: '12px 24px', borderRadius: '10px', background: 'linear-gradient(135deg, #06b6d4, #3b82f6)', border: 'none', color: '#fff', fontWeight: '700', cursor: 'pointer' }}>
                {isCalculating ? 'Computing Prediction...' : 'Calculate ML Prediction'}
              </button>

              {calcResult && (
                <div style={{ marginTop: '24px', padding: '20px', background: 'rgba(6, 182, 212, 0.1)', borderRadius: '12px', border: '1px solid rgba(6, 182, 212, 0.3)' }}>
                  <div style={{ fontSize: '1.2rem', fontWeight: '800', color: '#38bdf8' }}>
                    Probability P(Transfer): {(calcResult.transfer_probability * 100).toFixed(1)}%
                  </div>
                  <div style={{ marginTop: '8px', fontSize: '0.9rem' }}>
                    Transfer Intelligence Score: <strong>{calcResult.intelligence_score}/100</strong> ({calcResult.rating_label})
                  </div>
                  <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '8px' }}>{calcResult.disclaimer}</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* SYSTEM STATUS TAB */}
        {activeTab === 'system' && (
          <div className="glass-panel" style={{ padding: '28px' }}>
            <h3 style={{ fontSize: '1.2rem', fontWeight: '800', marginBottom: '20px' }}>Platform Diagnostics & System Status</h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '20px' }}>
              <div style={{ padding: '16px', background: 'rgba(255,255,255,0.03)', borderRadius: '12px' }}>
                <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Backend Version</div>
                <div style={{ fontSize: '1.2rem', fontWeight: '700' }}>v{healthStatus?.version || '1.0.0'}</div>
              </div>
              <div style={{ padding: '16px', background: 'rgba(255,255,255,0.03)', borderRadius: '12px' }}>
                <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>DuckDB Historical Engine</div>
                <div style={{ fontSize: '1.2rem', fontWeight: '700', color: '#10b981' }}>{healthStatus?.database_status || 'CONNECTED'}</div>
              </div>
              <div style={{ padding: '16px', background: 'rgba(255,255,255,0.03)', borderRadius: '12px' }}>
                <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>ML Models Active</div>
                <div style={{ fontSize: '1.2rem', fontWeight: '700', color: '#38bdf8' }}>Market Value, Fee & Probability</div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
