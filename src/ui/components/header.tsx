import { Activity } from "lucide-react";

export function Header() {
  return (
    <header className="bg-white shadow-sm border-b border-slate-200">
      <div className="px-6 py-4 flex justify-between items-center">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
            <Activity className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-slate-900">Spartis</h1>
            <p className="text-sm text-slate-500">BMD Viewer</p>
          </div>
        </div>
        <div className="flex items-center space-x-4">
          <div className="text-right">
            <p className="text-sm font-medium text-slate-900">Dr. Sarah Johnson</p>
            <p className="text-xs text-slate-500">Radiologist</p>
          </div>
          <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
            <span className="text-white font-medium text-sm">SJ</span>
          </div>
        </div>
      </div>
    </header>
  );
}