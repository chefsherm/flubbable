'use client';

import { useAgent } from '@/hooks/useAgent';
import { useBlueprintStore } from '@/store/blueprintStore';
import { ArchitectureGraph } from './ArchitectureGraph';
import { DatabaseDiff } from './DatabaseDiff';
import { TerminalView } from './TerminalView';

export function BlueprintView() {
  const { plan, status } = useBlueprintStore();
  const { approveBuild } = useAgent();

  // MODE 1: Terminal View (Building Phase)
  if (status === 'BUILDING' || status === 'DONE') {
    return <TerminalView />;
  }

  // MODE 2: Empty State
  if (!plan || status === 'IDLE' || status === 'PLANNING') {
    return (
      <div className="h-full flex flex-col items-center justify-center border-l border-gray-800 bg-gray-900 p-8">
        <div className="text-center max-w-md">
          {status === 'PLANNING' ? (
            <>
              <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mb-4"></div>
              <h2 className="text-xl font-bold text-white mb-2">
                🧠 AI is thinking...
              </h2>
              <p className="text-gray-400">
                Analyzing your request and generating technical blueprint
              </p>
            </>
          ) : (
            <>
              <svg
                className="mx-auto h-16 w-16 text-gray-600 mb-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
              </svg>
              <h2 className="text-xl font-bold text-white mb-2">
                No blueprint yet
              </h2>
              <p className="text-gray-400">
                Ask AI to generate a feature and the blueprint will appear here
              </p>
            </>
          )}
        </div>
      </div>
    );
  }

  // MODE 3: Blueprint Review (Negotiation Phase)
  const riskColor =
    plan.risk_audit.status === 'SAFE'
      ? 'green'
      : plan.risk_audit.status === 'WARNING'
      ? 'yellow'
      : 'red';

  const riskBgColor =
    plan.risk_audit.status === 'SAFE'
      ? 'bg-green-900/20 border-green-600'
      : plan.risk_audit.status === 'WARNING'
      ? 'bg-yellow-900/20 border-yellow-600'
      : 'bg-red-900/20 border-red-600';

  return (
    <div className="h-full flex flex-col border-l border-gray-800 bg-gray-900">
      {/* 1. Header with Status */}
      <div className="p-4 border-b border-gray-800 flex justify-between items-center">
        <h2 className="text-xl font-bold text-white">Project Blueprint</h2>
        <span
          className={`px-3 py-1 rounded-full text-sm font-semibold border ${riskBgColor} text-${riskColor}-400`}
        >
          {plan.risk_audit.status === 'SAFE' ? '✅ Ready to Build' : '⚠️ Risks Detected'}
        </span>
      </div>

      {/* 2. Tabs Content (Simplified - using direct sections) */}
      <div className="flex-1 overflow-y-auto p-4 space-y-6">
        {/* Architecture Section */}
        <div>
          <h3 className="text-lg font-semibold text-white mb-3">Architecture</h3>
          <ArchitectureGraph nodes={plan.nodes} />
        </div>

        {/* Database Changes */}
        {plan.database_changes.length > 0 && (
          <div>
            <h3 className="text-lg font-semibold text-white mb-3">Database Changes</h3>
            <DatabaseDiff changes={plan.database_changes} />
          </div>
        )}

        {/* Risk Audit */}
        {plan.risk_audit.risks.length > 0 && (
          <div>
            <h3 className="text-lg font-semibold text-white mb-3">Risk Assessment</h3>
            <div className={`p-4 rounded-lg border ${riskBgColor}`}>
              <ul className="space-y-2">
                {plan.risk_audit.risks.map((risk, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-gray-300">
                    <span className="text-yellow-500 mt-0.5">⚠️</span>
                    <span>{risk}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}
      </div>

      {/* 3. The Handshake (Bottom Bar) */}
      <div className="p-4 border-t border-gray-800 bg-black">
        <div className="flex justify-between items-center mb-3">
          <span className="text-sm text-gray-400">Estimated Effort</span>
          <span className="text-lg font-bold text-white">
            {plan.cost_estimate.toLocaleString()} tokens
          </span>
        </div>

        <button
          onClick={() => approveBuild(plan)}
          disabled={plan.risk_audit.status === 'CRITICAL'}
          className={`w-full py-3 px-4 rounded-lg font-semibold text-white transition-colors ${
            plan.risk_audit.status === 'CRITICAL'
              ? 'bg-gray-700 cursor-not-allowed opacity-50'
              : 'bg-green-600 hover:bg-green-700'
          }`}
        >
          {plan.risk_audit.status === 'CRITICAL'
            ? '❌ Cannot Build - Critical Risks'
            : '✅ Approve & Build'}
        </button>

        {plan.risk_audit.status === 'CRITICAL' && (
          <p className="mt-2 text-xs text-red-400 text-center">
            Please address critical risks before proceeding
          </p>
        )}
      </div>
    </div>
  );
}
