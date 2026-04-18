import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Amplify, Auth, API, graphqlOperation } from 'aws-amplify';
import { Authenticator, useAuthenticator } from '@aws-amplify/ui-react';
import { 
  RefreshCw, 
  MapPin, 
  Activity, 
  LogOut, 
  Bell, 
  AlertTriangle, 
  Users, 
  Zap,
  LayoutDashboard,
  ShieldAlert,
  X,
  Siren
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import awsConfig from './aws-config';

// UI Components
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertTitle, AlertDescription } from "@/components/ui/alert";
import { Skeleton } from "@/components/ui/skeleton";
import { Separator } from "@/components/ui/separator";

import '@aws-amplify/ui-react/styles.css';
import './index.css';

// Configure Amplify with Cookie Storage for enhanced security
Amplify.configure({
  ...awsConfig,
  Auth: {
    ...awsConfig.Auth,
    cookieStorage: {
      domain: window.location.hostname,
      path: '/',
      expires: 365,
      sameSite: "strict",
      secure: window.location.protocol === 'https:'
    }
  },
  // Unified API configuration for both REST and GraphQL
  API: {
    ...awsConfig.API,
    graphql_endpoint: awsConfig.aws_appsync_graphqlEndpoint,
    graphql_region: awsConfig.aws_appsync_region,
    graphql_authenticationType: awsConfig.aws_appsync_authenticationType,
  }
});

interface Zone {
  zoneId: string;
  crowdCount: number;
  capacity: number;
  status: 'Normal' | 'Busy' | 'Critical';
  action: string;
  lastUpdated: string;
}

// Static venue capacity per zone (could be stored in DynamoDB in production)
const DEFAULT_CAPACITY = 100;

interface CriticalNotification {
  id: string;
  zoneId: string;
  crowdCount: number;
  action: string;
  timestamp: Date;
  recommendedZoneId?: string;
  recommendedZonePercent?: number;
}

// ─── Critical Alert Toast ────────────────────────────────────────────────────
const CriticalAlertToast: React.FC<{
  notification: CriticalNotification;
  onDismiss: (id: string) => void;
}> = ({ notification, onDismiss }) => {
  useEffect(() => {
    const timer = setTimeout(() => onDismiss(notification.id), 8000);
    return () => clearTimeout(timer);
  }, [notification.id, onDismiss]);

  return (
    <motion.div
      layout
      initial={{ opacity: 0, x: 80, scale: 0.95 }}
      animate={{ opacity: 1, x: 0, scale: 1 }}
      exit={{ opacity: 0, x: 80, scale: 0.9 }}
      transition={{ type: 'spring', stiffness: 400, damping: 30 }}
      className="relative w-[340px] bg-white border-2 border-red-100 rounded-2xl shadow-2xl shadow-red-500/10 overflow-hidden"
    >
      {/* Animated red top bar */}
      <div className="h-1 w-full bg-gradient-to-r from-red-600 via-red-400 to-orange-500 animate-pulse" />

      <div className="p-5">
        <div className="flex items-start gap-4">
          {/* Icon */}
          <div className="shrink-0 bg-red-50 border border-red-100 rounded-xl p-2.5">
            <Siren size={18} className="text-red-500 animate-pulse" />
          </div>

          {/* Content */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between gap-2 mb-1">
              <span className="text-[9px] font-black uppercase tracking-[0.25em] text-red-500">
                Critical Alert
              </span>
              <span className="text-[9px] text-slate-400 font-bold">
                {notification.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </span>
            </div>
            <p className="text-sm font-bold text-slate-900 leading-tight">
              Zone <span className="text-red-600">{notification.zoneId}</span> exceeded capacity
            </p>
            <p className="text-xs text-slate-500 font-medium mt-1">
              {notification.crowdCount} occupants · {notification.action}
            </p>

            {/* NEW: Re-direction Recommendation */}
            {notification.recommendedZoneId && (
              <div className="mt-4 pt-4 border-t border-slate-100">
                <div className="flex items-center gap-1.5 mb-1.5">
                  <MapPin size={10} className="text-emerald-500" />
                  <span className="text-[9px] font-bold uppercase tracking-widest text-emerald-600">
                    Diversion Recommended
                  </span>
                </div>
                <div className="bg-emerald-50/50 rounded-xl p-2.5 border border-emerald-100/50 flex items-center justify-between gap-3">
                  <span className="text-xs font-bold text-emerald-700 whitespace-nowrap">Alternative: {notification.recommendedZoneId}</span>
                  <div className="shrink-0 flex items-center gap-1 bg-white px-2 py-0.5 rounded-full border border-emerald-200 shadow-sm">
                    <span className="text-[10px] font-black text-emerald-600">{notification.recommendedZonePercent}%</span>
                    <span className="text-[8px] font-bold text-emerald-400 uppercase tracking-tighter">Cap</span>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Dismiss */}
          <button
            onClick={() => onDismiss(notification.id)}
            className="shrink-0 text-slate-300 hover:text-slate-500 transition-colors p-1 rounded-lg hover:bg-slate-50"
          >
            <X size={14} />
          </button>
        </div>
      </div>

      {/* Auto-dismiss progress bar */}
      <motion.div
        className="h-[3px] bg-red-400/30 origin-left"
        initial={{ scaleX: 1 }}
        animate={{ scaleX: 0 }}
        transition={{ duration: 8, ease: 'linear' }}
      />
    </motion.div>
  );
};

// ─── Notification Panel (Bell) ───────────────────────────────────────────────
const NotificationBell: React.FC<{
  count: number;
  notifications: CriticalNotification[];
  onDismissAll: () => void;
}> = ({ count, notifications, onDismissAll }) => {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  return (
    <div className="relative" ref={ref}>
      <button
        onClick={() => setOpen(o => !o)}
        className="relative p-2.5 rounded-xl hover:bg-red-50 transition-all group"
        aria-label="Critical Alerts"
      >
        <Bell size={16} className={count > 0 ? 'text-red-500' : 'text-slate-400'} />
        <AnimatePresence>
          {count > 0 && (
            <motion.span
              key="badge"
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              exit={{ scale: 0 }}
              className="absolute -top-0.5 -right-0.5 h-4 w-4 flex items-center justify-center rounded-full bg-red-500 text-white text-[9px] font-black"
            >
              {count > 9 ? '9+' : count}
            </motion.span>
          )}
        </AnimatePresence>
      </button>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, y: -8, scale: 0.96 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -8, scale: 0.96 }}
            transition={{ duration: 0.15 }}
            className="absolute right-0 top-12 w-[320px] bg-white border border-slate-100 rounded-2xl shadow-2xl shadow-slate-200/50 z-[200] overflow-hidden"
          >
            <div className="flex items-center justify-between px-5 py-4 border-b border-slate-50">
              <span className="text-sm font-bold text-slate-900">Active Incidents</span>
              {notifications.length > 0 && (
                <button onClick={onDismissAll} className="text-[10px] font-bold text-primary hover:text-primary/70 transition-colors uppercase tracking-widest">
                  Clear all
                </button>
              )}
            </div>

            <div className="max-h-[300px] overflow-y-auto">
              {notifications.length === 0 ? (
                <div className="px-5 py-8 text-center">
                  <div className="w-10 h-10 bg-emerald-50 rounded-full flex items-center justify-center mx-auto mb-3">
                    <Activity size={18} className="text-emerald-500" />
                  </div>
                  <p className="text-xs font-bold text-slate-400 uppercase tracking-widest">All Clear</p>
                  <p className="text-[11px] text-slate-300 mt-1">No critical incidents</p>
                </div>
              ) : (
                notifications.map(n => (
                  <div key={n.id} className="px-5 py-3.5 border-b border-slate-50 last:border-0 hover:bg-red-50/30 transition-colors">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-[9px] font-black uppercase tracking-[0.2em] text-red-500">{n.zoneId}</span>
                      <span className="text-[9px] text-slate-400">{n.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                    </div>
                    <p className="text-xs font-bold text-slate-800">{n.crowdCount} occupants — {n.action}</p>
                    {n.recommendedZoneId && (
                      <div className="mt-2 flex items-center gap-1.5 text-[9px] font-bold text-emerald-600 bg-emerald-50 w-fit px-2 py-0.5 rounded-md">
                        <MapPin size={8} />
                        Redirect to {n.recommendedZoneId}
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

// ─── Dashboard ───────────────────────────────────────────────────────────────
const Dashboard: React.FC = () => {
  const { user, signOut } = useAuthenticator((context) => [context.user]);
  const [zones, setZones] = useState<Zone[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Notification state
  const [toasts, setToasts] = useState<CriticalNotification[]>([]);
  const [history, setHistory] = useState<CriticalNotification[]>([]);
  const prevZonesRef = useRef<Map<string, 'Normal' | 'Busy' | 'Critical'>>(new Map());

  const dismissToast = useCallback((id: string) => {
    setToasts(t => t.filter(n => n.id !== id));
  }, []);

  const dismissAll = useCallback(() => {
    setToasts([]);
    setHistory([]);
  }, []);

  const onUpdateZone = `
    subscription OnUpdateZone {
      onUpdateZone {
        zoneId
        crowdCount
        capacity
        status
        action
        lastUpdated
      }
    }
  `;

  const calculateStatus = (count: number, capacity: number): 'Normal' | 'Busy' | 'Critical' => {
    const pct = (count / capacity) * 100;
    if (pct >= 90) return 'Critical';
    if (pct >= 70) return 'Busy';
    return 'Normal';
  };

  const processUpdate = useCallback((updatedZone: any) => {
    setZones(prev => {
      const idx = prev.findIndex(z => z.zoneId === updatedZone.zoneId);
      const newStatus = calculateStatus(updatedZone.crowdCount, updatedZone.capacity);
      const newZone = { 
        ...updatedZone, 
        status: newStatus,
        action: newStatus === 'Critical' ? 'Restrict Entry / Redirect Flow' : 'No Action'
      };

      if (newStatus === 'Critical') {
        const recommendation = findBestRedirectionZone(prev, newZone.zoneId);
        const notification: CriticalNotification = {
          id: Math.random().toString(36).substr(2, 9),
          zoneId: newZone.zoneId,
          crowdCount: newZone.crowdCount,
          action: newZone.action,
          timestamp: new Date(),
          recommendedZoneId: recommendation?.zoneId,
          recommendedZonePercent: recommendation?.occupancyPercent
        };
        setToasts(t => [...t, notification].slice(-3));
        setHistory(h => [notification, ...h].slice(0, 50));
      }

      if (idx === -1) return [...prev, newZone];
      const next = [...prev];
      next[idx] = newZone;
      return next;
    });
  }, []);

  const listZones = `
    query ListZones {
      listZones {
        zoneId
        crowdCount
        capacity
        status
        action
        lastUpdated
      }
    }
  `;

  // ─── Predictive Redirection Logic ──────────────────────────────────────────
  const findBestRedirectionZone = (currentZones: Zone[], sourceId: string) => {
    // Candidates are zones that are NOT the critical one and are NOT themselves busy/critical
    const candidates = currentZones
      .filter(z => z.zoneId !== sourceId && z.status === 'Normal')
      .map(z => ({
        ...z,
        occupancyPercent: Math.round((z.crowdCount / z.capacity) * 100)
      }))
      .sort((a, b) => a.occupancyPercent - b.occupancyPercent);

    return candidates.length > 0 ? candidates[0] : null;
  };

  const fetchZones = async () => {
    setLoading(true);
    setError(null);
    try {
      console.log("DEBUG: Validating session for GraphQL Query...");
      const session = await Auth.currentSession();
      if (!session) throw new Error('Session expired');
      
      const token = session.getIdToken().getJwtToken();
      console.log("DEBUG: Session valid. Fetching initial state...");

      const response = await API.graphql({
        query: listZones,
        authToken: token
      }) as any;

      const data: Zone[] = response.data.listZones || [];
      console.log(`DEBUG: Successfully loaded ${data.length} zones.`);

      const newToasts: CriticalNotification[] = [];
      const processedZones = data.map((z: any) => {
        const zoneStatus = calculateStatus(z.crowdCount, z.capacity);
        const zone = {
          ...z,
          status: zoneStatus,
          action: zoneStatus === 'Critical' ? 'Restrict Entry / Redirect Flow' : 'No Action'
        };

        if (zone.status === 'Critical') {
          const recommendation = findBestRedirectionZone(data, zone.zoneId);
          newToasts.push({
            id: Math.random().toString(36).substr(2, 9),
            zoneId: zone.zoneId,
            crowdCount: zone.crowdCount,
            action: zone.action,
            timestamp: new Date(),
            recommendedZoneId: recommendation?.zoneId,
            recommendedZonePercent: recommendation?.occupancyPercent
          });
        }
        return zone;
      });

      if (newToasts.length > 0) {
        setToasts(t => [...t, ...newToasts].slice(-3));
        setHistory(h => [...newToasts, ...h].slice(0, 50));
      }

      // Update previous status map
      prevZonesRef.current = new Map(processedZones.map(z => [z.zoneId, z.status]));
      setZones(processedZones);
    } catch (err: any) {
      console.error('DEBUG ERROR: GraphQL Query Sync failed:', err);
      setError(err.message || 'Failed to fetch monitoring data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchZones(); // Initial load
    console.log("DEBUG: Initialising Real-time Cloud Bus connection...");

    // Subscribe to real-time updates
    const subscription = (API.graphql(
      graphqlOperation(onUpdateZone)
    ) as any).subscribe({
      next: ({ value }: any) => {
        console.log("DEBUG: Real-time update received!", value.data.onUpdateZone);
        const zone = value.data.onUpdateZone;
        processUpdate(zone);
      },
      error: (err: any) => {
        console.error('DEBUG ERROR: Subscription failed:', err);
        setError("Real-time connection interrupted. Please refresh.");
      }
    });

    return () => {
      console.log("DEBUG: Cleaning up subscription...");
      subscription.unsubscribe();
    };
  }, [onUpdateZone, processUpdate]);

  const totalPeople = zones.reduce((acc, z) => acc + z.crowdCount, 0);
  const criticalCount = zones.filter(z => z.status === 'Critical').length;
  const busyCount = zones.filter(z => z.status === 'Busy').length;

  return (
    <div className="min-h-screen bg-[#fffcfb] font-sans selection:bg-orange-100 selection:text-orange-900">

      {/* ── Toast Stack (top-right) ── */}
      <div className="fixed top-20 right-6 z-[300] flex flex-col gap-3 pointer-events-none">
        <AnimatePresence mode="popLayout">
          {toasts.map(n => (
            <div key={n.id} className="pointer-events-auto">
              <CriticalAlertToast notification={n} onDismiss={dismissToast} />
            </div>
          ))}
        </AnimatePresence>
      </div>

      {/* Navigation Header */}
      <nav className="sticky top-0 z-50 w-full border-b border-orange-100/30 glass">
        <div className="container flex h-16 items-center justify-between py-2 max-w-7xl mx-auto px-6">
          <div className="flex items-center gap-2.5">
            <div className="bg-primary p-2 rounded-xl shadow-lg shadow-primary/10 transition-transform duration-300 hover:scale-105">
              <Zap size={18} className="text-white" fill="currentColor" />
            </div>
            <div className="flex flex-col">
              <span className="text-xl font-display font-bold tracking-tight text-slate-900 leading-none">CrowdSync</span>
              <span className="text-[9px] text-primary/60 font-bold uppercase tracking-[0.3em] mt-1">Global Intelligence</span>
            </div>
          </div>

          <div className="flex items-center gap-4">
            {/* Notification Bell */}
            <NotificationBell
              count={history.length}
              notifications={history}
              onDismissAll={dismissAll}
            />

            <div className="hidden lg:flex flex-col items-end text-right border-r pr-6 border-orange-100/50">
              <span className="text-xs font-bold text-slate-900 leading-none">{user?.attributes?.email}</span>
              <span className="text-[9px] text-primary/40 font-bold uppercase tracking-widest leading-none mt-1">Operational Admin</span>
            </div>
            <Button variant="ghost" size="sm" onClick={signOut} className="h-9 px-4 rounded-lg text-slate-400 hover:text-primary hover:bg-primary/5 transition-all font-bold text-[9px] uppercase tracking-widest">
              <LogOut size={14} className="mr-2" />
              Exit
            </Button>
          </div>
        </div>
      </nav>

      <main className="container max-w-7xl mx-auto p-8 lg:p-12 space-y-12">
        {/* Page Header */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 pb-2">
          <div className="space-y-2">
            <h1 className="text-4xl lg:text-5xl font-display font-bold tracking-tight text-slate-900">Venue Control</h1>
            <p className="text-slate-400 text-base max-w-2xl font-medium leading-relaxed">
              Orchestrate venue operations with real-time occupancy telemetry and <span className="text-primary font-bold italic">predictive safety thresholds.</span>
            </p>
          </div>
          <Button
            onClick={fetchZones}
            disabled={loading}
            className="h-11 px-8 rounded-xl bg-slate-900 text-white hover:bg-primary shadow-xl shadow-slate-200/50 ring-4 ring-white transition-all transform hover:-translate-y-0.5 active:scale-95 text-xs font-bold uppercase tracking-widest"
          >
            <RefreshCw className={`mr-2.5 h-3.5 w-3.5 ${loading ? 'animate-spin' : ''}`} />
            Sync Telemetry
          </Button>
        </div>

        {/* Stats Summary */}
        <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-4">
          <StatCard title="Total Occupancy" value={totalPeople} icon={<Users className="text-primary" />} subtitle="Across active zones" loading={loading} />
          <StatCard title="Critical Zones" value={criticalCount} icon={<ShieldAlert className={criticalCount > 0 ? 'text-red-500' : 'text-primary/30'} />} subtitle="Require response" loading={loading} highlight={criticalCount > 0} />
          <StatCard title="Density Alerts" value={busyCount} icon={<Bell className="text-orange-500" />} subtitle="High capacity" loading={loading} />
          <StatCard title="Network Status" value="Active" icon={<Activity className="text-primary" />} subtitle={awsConfig.Auth.region} loading={loading} />
        </div>

        {error && (
          <Alert variant="destructive" className="border-red-100 bg-red-50/30 rounded-[2rem] p-8 shadow-sm border-2 animate-in fade-in zoom-in-95">
            <AlertTriangle className="h-6 w-6 text-primary" />
            <AlertTitle className="font-display font-black text-xl text-slate-900">Security Handshake Interrupted</AlertTitle>
            <AlertDescription className="font-bold text-primary/60 mt-2 text-sm leading-relaxed">{error}. Attempting to re-establish secure link.</AlertDescription>
          </Alert>
        )}

        {/* Zones Grid */}
        <div className="space-y-8 pb-16">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2.5 bg-white shadow-xl shadow-orange-500/5 rounded-xl border border-orange-50"><LayoutDashboard size={20} className="text-primary" /></div>
              <h2 className="text-2xl font-display font-bold tracking-tight text-slate-800">Zone Monitor</h2>
            </div>
            <Badge variant="outline" className="px-3 py-1 bg-primary/5 border-primary/10 text-primary font-bold uppercase tracking-[0.2em] text-[8px] rounded-lg">Stream Live</Badge>
          </div>

          <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
            <AnimatePresence mode="popLayout">
              {loading && zones.length === 0 ? (
                Array.from({ length: 6 }).map((_, i) => (
                  <Card key={`skeleton-${i}`} className="h-64 rounded-[2.5rem] border-none shadow-sm animate-pulse bg-slate-50/50" />
                ))
              ) : (
                zones.map((zone) => (
                  <motion.div
                    layout
                    key={zone.zoneId}
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.9 }}
                    transition={{ type: "spring", stiffness: 300, damping: 30 }}
                  >
                    <Card className={`group relative overflow-hidden rounded-2xl border-none shadow-[0_8px_30px_rgba(15,23,42,0.02)] hover:shadow-[0_20px_45px_rgba(249,115,22,0.1)] transition-all duration-500 bg-white ${zone.status === 'Critical' ? 'ring-2 ring-red-200' : ''}`}>
                      {zone.status === 'Critical' && (
                        <div className="h-0.5 w-full bg-gradient-to-r from-red-600 via-red-400 to-orange-500 animate-pulse" />
                      )}
                      <div className="p-8 space-y-6">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2 px-3 py-1.5 bg-slate-50 rounded-lg border border-slate-100 group-hover:bg-white transition-colors">
                            <MapPin size={11} className="text-primary" />
                            <span className="text-[9px] font-bold text-slate-500 uppercase tracking-widest">{zone.zoneId}</span>
                          </div>
                          <Badge
                            variant={zone.status === 'Critical' ? 'destructive' : zone.status === 'Busy' ? 'secondary' : 'outline'}
                            className={`px-3 py-0.5 rounded-lg font-bold uppercase tracking-widest text-[8px] border-2 border-white shadow-sm ${
                              zone.status === 'Normal' ? 'text-emerald-500 bg-emerald-50' :
                              zone.status === 'Busy' ? 'text-orange-500 bg-orange-50' : ''
                            }`}
                          >
                            {zone.status}
                          </Badge>
                        </div>

                        <div className="space-y-0.5">
                          <div className="text-6xl font-display font-bold text-slate-900 tracking-tighter flex items-baseline gap-2.5 leading-none">
                            {zone.crowdCount}
                            <span className="text-[10px] font-bold text-slate-300 uppercase tracking-widest">Occupants</span>
                          </div>
                        </div>

                        {/* Capacity Bar */}
                        {(() => {
                          const cap = zone.capacity ?? DEFAULT_CAPACITY;
                          const pct = Math.min(100, Math.round((zone.crowdCount / cap) * 100));
                          const barColor =
                            zone.status === 'Critical' ? 'bg-red-500' :
                            zone.status === 'Busy'     ? 'bg-orange-400' : 'bg-emerald-400';
                          return (
                            <div className="space-y-1.5">
                              <div className="flex items-center justify-between">
                                <span className="text-[9px] font-bold text-slate-400 uppercase tracking-widest">Capacity</span>
                                <span className={`text-[9px] font-black tabular-nums ${
                                  zone.status === 'Critical' ? 'text-red-500' :
                                  zone.status === 'Busy' ? 'text-orange-500' : 'text-emerald-500'
                                }`}>
                                  {zone.crowdCount} / {cap} &nbsp;·&nbsp; {pct}%
                                </span>
                              </div>
                              <div className="h-1.5 w-full bg-slate-100 rounded-full overflow-hidden">
                                <motion.div
                                  className={`h-full rounded-full ${barColor}`}
                                  initial={{ width: 0 }}
                                  animate={{ width: `${pct}%` }}
                                  transition={{ duration: 0.6, ease: 'easeOut' }}
                                />
                              </div>
                            </div>
                          );
                        })()}

                        <div className={`p-4 rounded-xl border transition-all ${
                          zone.status === 'Critical' ? 'bg-red-50 border-red-100 text-red-900 shadow-md shadow-red-100/30' :
                          zone.status === 'Busy' ? 'bg-orange-50 border-orange-100 text-orange-900' :
                          'bg-slate-50 border-slate-100 text-slate-600'
                        }`}>
                          <div className={`text-[8px] font-bold uppercase tracking-[0.15em] mb-1.5 opacity-40 ${zone.status === 'Normal' ? 'text-primary' : ''}`}>Primary Response</div>
                          <p className="text-xs font-bold leading-relaxed">{zone.action}</p>
                        </div>
                      </div>

                      <div className="px-8 py-4 bg-slate-50/30 border-t border-slate-50 flex justify-between items-center group-hover:bg-white transition-colors">
                        <span className="text-[9px] font-bold text-slate-400 uppercase tracking-widest flex items-center gap-1.5">
                          <RefreshCw size={10} className="text-primary/30" />
                          {new Date(zone.lastUpdated).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </span>
                        <div className={`h-1.5 w-1.5 rounded-full ${
                          zone.status === 'Critical' ? 'bg-red-500 animate-pulse' :
                          zone.status === 'Busy' ? 'bg-orange-500' : 'bg-emerald-500'
                        }`} />
                      </div>
                    </Card>
                  </motion.div>
                ))
              )}
            </AnimatePresence>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="fixed bottom-0 w-full glass border-t border-slate-200/50 py-3 px-8 z-50">
        <div className="container max-w-7xl mx-auto flex justify-between items-center text-[10px] text-slate-400 font-black uppercase tracking-[0.3em] font-display">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-1.5">
              <span className="h-2 w-2 rounded-full bg-emerald-500" />
              Link Integrity Confirmed
            </div>
            <Separator orientation="vertical" className="h-3 bg-slate-200" />
            <span className="opacity-60">System Ready for Deployment</span>
          </div>
          <div className="opacity-80">Secured via AWS Virtual Private Cloud</div>
        </div>
      </footer>
    </div>
  );
};

// ─── Stat Card ───────────────────────────────────────────────────────────────
const StatCard: React.FC<{
  title: string;
  value: string | number;
  icon: React.ReactNode;
  subtitle: string;
  loading?: boolean;
  highlight?: boolean;
}> = ({ title, value, icon, subtitle, loading, highlight }) => (
  <Card className={`relative overflow-hidden rounded-2xl border border-slate-50 shadow-sm p-6 transition-all hover:shadow-md group bg-white ${highlight ? 'ring-1 ring-red-100 bg-red-50/5' : ''}`}>
    <div className="flex flex-row items-center justify-between mb-5">
      <span className="text-[10px] font-bold text-slate-400 uppercase tracking-[0.15em]">{title}</span>
      <div className="p-2.5 bg-slate-50 rounded-xl group-hover:scale-110 transition-transform">
        {React.cloneElement(icon as React.ReactElement, { size: 16 })}
      </div>
    </div>
    <div className="space-y-0.5">
      <div className="text-2xl font-display font-bold text-slate-900 tracking-tight">
        {loading ? <Skeleton className="h-8 w-20" /> : value}
      </div>
      <div className="text-[9px] font-bold text-slate-300 tracking-[0.05em] uppercase">{subtitle}</div>
    </div>
  </Card>
);


import { AuthCenter } from './components/auth-center';

const App: React.FC = () => {
  return (
    <Authenticator.Provider>
      <AppContent />
    </Authenticator.Provider>
  );
};

const AppContent: React.FC = () => {
  const { authStatus } = useAuthenticator(context => [context.authStatus]);

  if (authStatus === 'authenticated') {
    return <Dashboard />;
  }

  if (authStatus === 'unauthenticated') {
    return <AuthCenter />;
  }

  return (
    <div className="min-h-screen bg-[#fcfdfe] flex items-center justify-center">
      <div className="flex flex-col items-center gap-4">
        <div className="bg-primary p-2.5 rounded-2xl animate-pulse">
          <Zap size={28} className="text-white" fill="currentColor" />
        </div>
        <p className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] animate-pulse">
          Securing Link...
        </p>
      </div>
    </div>
  );
};

export default App;
