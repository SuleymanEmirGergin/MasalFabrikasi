import { Component, type ErrorInfo, type ReactNode } from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

/**
 * Catches React render errors and shows a fallback UI so the app does not white-screen.
 */
export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false, error: null };

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    console.error('ErrorBoundary caught:', error, errorInfo);
  }

  handleRetry = (): void => {
    this.setState({ hasError: false, error: null });
  };

  render(): ReactNode {
    if (this.state.hasError && this.state.error) {
      if (this.props.fallback) return this.props.fallback;
      return (
        <div className="min-h-screen bg-[#02010a] flex items-center justify-center p-6">
          <div className="max-w-md w-full text-center space-y-6">
            <div className="p-4 rounded-2xl bg-red-500/10 border border-red-500/20 inline-flex">
              <AlertTriangle className="w-12 h-12 text-red-400" />
            </div>
            <h1 className="text-xl font-bold text-white">Bir şeyler yanlış gitti</h1>
            <p className="text-slate-400 text-sm">
              Beklenmeyen bir hata oluştu. Sayfayı yenileyerek tekrar deneyebilirsiniz.
            </p>
            <pre className="text-left text-xs text-slate-500 bg-white/5 rounded-lg p-3 overflow-auto max-h-24">
              {this.state.error.message}
            </pre>
            <Button
              onClick={this.handleRetry}
              className="bg-magical-indigo hover:bg-magical-indigo/90 text-white"
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              Tekrar dene
            </Button>
            <Button
              variant="ghost"
              className="text-slate-400"
              onClick={() => window.location.href = '/'}
            >
              Ana sayfaya dön
            </Button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}
