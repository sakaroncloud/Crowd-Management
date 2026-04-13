import React, { useState } from 'react';
import { Auth } from 'aws-amplify';
import { 
  Card, 
  CardContent, 
  CardDescription, 
  CardFooter, 
  CardHeader, 
  CardTitle 
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Zap, AlertCircle, ArrowLeft, Key, Mail } from 'lucide-react';

type AuthView = 'sign-in' | 'forgot-password' | 'reset-password' | 'challenge-new-password';

export const AuthCenter: React.FC = () => {
  const [view, setView] = useState<AuthView>('sign-in');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [code, setCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [challengeUser, setChallengeUser] = useState<any>(null);

  const handleSignIn = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const user = await Auth.signIn(email, password);
      
      if (user.challengeName === 'NEW_PASSWORD_REQUIRED') {
        setChallengeUser(user);
        setView('challenge-new-password');
        setPassword(''); // Clear the temporary password
      }
    } catch (err: any) {
      setError(err.message || 'Authentication failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  const handleRequestReset = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await Auth.forgotPassword(email);
      setView('reset-password');
    } catch (err: any) {
      setError(err.message || 'Could not initiate password reset.');
    } finally {
      setLoading(false);
    }
  };

  const handleResetSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await Auth.forgotPasswordSubmit(email, code, password);
      setView('sign-in');
      setPassword('');
      setError('Password reset successfully. You can now sign in.');
    } catch (err: any) {
      setError(err.message || 'Could not reset password. Check the code and try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleCompleteNewPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await Auth.completeNewPassword(challengeUser, password);
      // Auth status will automatically update to 'authenticated' via App.tsx
    } catch (err: any) {
      setError(err.message || 'Could not set new password.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#fffcfb] flex flex-col items-center justify-center p-6 selection:bg-orange-100 relative overflow-hidden">
      {/* Executive Warm Accents */}
      <div className="absolute top-0 right-0 w-[60vw] h-[60vh] bg-orange-100/30 blur-[130px] rounded-full -translate-y-1/2 translate-x-1/2" />
      <div className="absolute bottom-0 left-0 w-[50vw] h-[50vh] bg-red-100/20 blur-[130px] rounded-full translate-y-1/2 -translate-x-1/2" />

      <div className="w-full max-w-[440px] relative z-10 transition-all duration-1000 animate-in fade-in slide-in-from-bottom-8">
        <div className="flex flex-col items-center justify-center mb-10">
          <div className="bg-primary p-2.5 rounded-2xl shadow-xl shadow-primary/20 mb-5 transition-transform duration-500 hover:scale-105">
            <Zap size={24} className="text-white" fill="currentColor" />
          </div>
          <h1 className="text-4xl font-display font-bold tracking-tight text-slate-900">CrowdSync</h1>
          <p className="text-primary/60 font-bold uppercase tracking-[0.4em] text-[9px] mt-2">Management Systems</p>
        </div>

        <Card className="border-none shadow-[0_15px_40px_rgba(249,115,22,0.06)] bg-white/90 backdrop-blur-xl overflow-hidden rounded-[2rem]">
          {view === 'sign-in' && (
            <div className="animate-in fade-in slide-in-from-left-6 duration-700 p-1">
              <CardHeader className="space-y-1.5 pt-8 pb-5 px-8 text-center">
                <CardTitle className="text-2xl font-bold text-slate-900">Sign In</CardTitle>
                <CardDescription className="text-xs font-medium text-slate-400">
                  Access the venue telemetry portal.
                </CardDescription>
              </CardHeader>
              <form onSubmit={handleSignIn}>
                <CardContent className="space-y-5 pt-1 px-8">
                  {error && (
                    <Alert variant={error.includes('successfully') ? 'default' : 'destructive'} className="py-3 rounded-xl border-2">
                      <AlertCircle className="h-4 w-4" />
                      <AlertDescription className="text-[10px] font-bold leading-relaxed">{error}</AlertDescription>
                    </Alert>
                  )}
                  <div className="space-y-2.5">
                    <Label htmlFor="email-input" className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">Administrative Email</Label>
                    <Input 
                      id="email-input" 
                      type="email" 
                      placeholder="admin@crowdsync.com" 
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      required
                      className="h-11 bg-white border-slate-100 rounded-xl shadow-sm focus:border-primary transition-all px-4 text-sm"
                      aria-label="Executive Email Address"
                    />
                  </div>
                  <div className="space-y-2.5">
                    <div className="flex items-center justify-between">
                      <Label htmlFor="password-input" className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">Security Password</Label>
                      <button 
                        type="button" 
                        id="forgot-password-link"
                        onClick={() => setView('forgot-password')}
                        className="text-[9px] font-bold uppercase tracking-widest text-primary hover:text-primary/80 transition-colors"
                        aria-label="Initiate Password Recovery"
                      >
                        Recovery?
                      </button>
                    </div>
                    <Input 
                      id="password-input" 
                      type="password" 
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      required
                      className="h-11 bg-white border-slate-100 rounded-xl shadow-sm focus:border-primary transition-all px-4 text-sm"
                      aria-label="Executive Security Password"
                    />
                  </div>
                </CardContent>
                <CardFooter className="pb-10 pt-6 px-8">
                  <Button id="sign-in-button" type="submit" className="w-full h-11 rounded-xl text-xs font-bold uppercase tracking-widest shadow-lg shadow-primary/10 hover:shadow-primary/20 transition-all duration-300" disabled={loading}>
                    {loading ? 'Securing Link...' : 'Authorize Access'}
                  </Button>
                </CardFooter>
              </form>
            </div>
          )}

          {view === 'forgot-password' && (
            <div className="animate-in fade-in slide-in-from-right-6 duration-700 p-2">
                <CardHeader className="space-y-1.5 pt-8 pb-5 px-8">
                <div className="flex items-center gap-3 mb-2">
                  <button 
                    onClick={() => setView('sign-in')}
                    className="p-1.5 hover:bg-slate-50 rounded-lg text-slate-400 hover:text-primary transition-all"
                  >
                    <ArrowLeft size={18} />
                  </button>
                  <CardTitle className="text-2xl font-bold text-slate-900">Recovery</CardTitle>
                </div>
                <CardDescription className="text-xs font-medium text-slate-400">
                  Enter your email to receive a recovery code.
                </CardDescription>
              </CardHeader>
              <form onSubmit={handleRequestReset}>
                <CardContent className="space-y-5 pt-1 px-8">
                  {error && (
                    <Alert variant="destructive" className="py-3 rounded-xl border-2">
                      <AlertCircle className="h-4 w-4" />
                      <AlertDescription className="text-[10px] font-bold">{error}</AlertDescription>
                    </Alert>
                  )}
                  <div className="space-y-2.5">
                    <Label htmlFor="reset-email" className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">Administrative Email</Label>
                    <div className="relative">
                      <Mail className="absolute left-4 top-3.5 h-4 w-4 text-slate-300" />
                      <Input 
                        id="reset-email" 
                        type="email" 
                        placeholder="admin@crowdsync.com" 
                        className="h-11 pl-11 bg-white border-slate-100 rounded-xl text-sm"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                      />
                    </div>
                  </div>
                </CardContent>
                <CardFooter className="pb-10 pt-6 px-8">
                  <Button type="submit" className="w-full h-11 rounded-xl text-xs font-bold uppercase tracking-widest shadow-lg shadow-primary/10" disabled={loading}>
                    {loading ? 'Transmitting...' : 'Begin Recovery'}
                  </Button>
                </CardFooter>
              </form>
            </div>
          )}

          {view === 'reset-password' && (
            <div className="animate-in fade-in slide-in-from-right-6 duration-700 p-2">
              <CardHeader className="space-y-1.5 pt-8 pb-5 px-8">
                <CardTitle className="text-2xl font-bold text-slate-900">New Password</CardTitle>
                <CardDescription className="text-xs font-medium text-slate-400">
                  Check verification code in **{email}**.
                </CardDescription>
              </CardHeader>
              <form onSubmit={handleResetSubmit}>
                <CardContent className="space-y-5 pt-1 px-8">
                  {error && (
                    <Alert variant="destructive" className="py-3 rounded-xl border-2">
                      <AlertCircle className="h-4 w-4" />
                      <AlertDescription className="text-[10px] font-bold">{error}</AlertDescription>
                    </Alert>
                  )}
                  <div className="space-y-2.5">
                    <Label htmlFor="code" className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">Verification Code</Label>
                    <div className="relative">
                      <Key className="absolute left-4 top-3.5 h-4 w-4 text-slate-300" />
                      <Input 
                        id="code" 
                        placeholder="6-digit code" 
                        maxLength={6}
                        className="h-11 pl-11 bg-white border-slate-100 rounded-xl font-mono text-base tracking-[0.4em]"
                        value={code}
                        onChange={(e) => setCode(e.target.value)}
                        required
                      />
                    </div>
                  </div>
                  <div className="space-y-2.5">
                    <Label htmlFor="new-password" className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">Secure New Password</Label>
                    <Input 
                      id="new-password" 
                      type="password" 
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      required
                      className="h-11 bg-white border-slate-100 rounded-xl px-4 text-sm"
                    />
                  </div>
                </CardContent>
                <CardFooter className="pb-10 pt-6 px-8">
                  <Button type="submit" className="w-full h-11 rounded-xl text-xs font-bold uppercase tracking-widest" disabled={loading}>
                    {loading ? 'Re-writing...' : 'Update & Sign In'}
                  </Button>
                </CardFooter>
              </form>
            </div>
          )}
          {view === 'challenge-new-password' && (
            <div className="animate-in fade-in slide-in-from-right-6 duration-700 p-2">
              <CardHeader className="space-y-1.5 pt-8 pb-5 px-8 text-center">
                <CardTitle className="text-2xl font-bold text-slate-900">Security Upgrade</CardTitle>
                <CardDescription className="text-xs font-medium text-slate-400">
                  A permanent password is required for your account.
                </CardDescription>
              </CardHeader>
              <form onSubmit={handleCompleteNewPassword}>
                <CardContent className="space-y-5 pt-1 px-8">
                  {error && (
                    <Alert variant="destructive" className="py-3 rounded-xl border-2">
                      <AlertCircle className="h-4 w-4" />
                      <AlertDescription className="text-[10px] font-bold">{error}</AlertDescription>
                    </Alert>
                  )}
                  <div className="space-y-2.5">
                    <Label htmlFor="new-permanent-password" className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">Set Permanent Password</Label>
                    <div className="relative">
                      <Key className="absolute left-4 top-3.5 h-4 w-4 text-slate-300" />
                      <Input 
                        id="new-permanent-password" 
                        type="password" 
                        placeholder="Min. 8 chars + special" 
                        className="h-11 pl-11 bg-white border-slate-100 rounded-xl text-sm"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                      />
                    </div>
                  </div>
                </CardContent>
                <CardFooter className="pb-10 pt-6 px-8">
                  <Button type="submit" className="w-full h-11 rounded-xl text-xs font-bold uppercase tracking-widest shadow-lg shadow-primary/10" disabled={loading}>
                    {loading ? 'Finalizing Setup...' : 'Establish Security Profile'}
                  </Button>
                </CardFooter>
              </form>
            </div>
          )}
        </Card>

        <div className="text-center mt-12 space-y-4">
          <div className="h-[1px] w-16 bg-gradient-to-r from-transparent via-slate-200 to-transparent mx-auto" />
          <p className="text-[10px] font-black text-slate-300 uppercase tracking-widest leading-loose">
            Authorized Executive Access<br/>
            <span className="text-primary/30 font-bold">Encrypted via AWS Global Shield</span>
          </p>
        </div>
      </div>
    </div>
  );
};
