'use client';

import { useEffect, useRef } from 'react';
import { useBlueprintStore } from '@/store/blueprintStore';

export function TerminalView() {
  const { terminalLogs, status } = useBlueprintStore();
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new logs arrive
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [terminalLogs]);

  return (
    <div className="h-full flex flex-col bg-black border-l border-gray-800">
      {/* Terminal Header */}
      <div className="flex items-center justify-between px-4 py-2 bg-gray-900 border-b border-gray-800">
        <div className="flex items-center gap-2">
          <div className="flex gap-1.5">
            <div className="w-3 h-3 rounded-full bg-red-500"></div>
            <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
            <div className="w-3 h-3 rounded-full bg-green-500"></div>
          </div>
          <span className="text-sm font-mono text-gray-400">terminal</span>
        </div>

        <div className="flex items-center gap-2">
          {status === 'BUILDING' && (
            <>
              <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
              <span className="text-xs font-mono text-green-400">BUILDING...</span>
            </>
          )}
          {status === 'DONE' && (
            <>
              <div className="w-2 h-2 rounded-full bg-blue-500"></div>
              <span className="text-xs font-mono text-blue-400">COMPLETE</span>
            </>
          )}
        </div>
      </div>

      {/* Terminal Content */}
      <div
        ref={scrollRef}
        className="flex-1 overflow-y-auto p-4 font-mono text-sm"
      >
        {terminalLogs.length === 0 ? (
          <div className="text-gray-600">
            <span className="text-green-400">$</span> Waiting for logs...
          </div>
        ) : (
          <div className="space-y-1">
            {terminalLogs.map((log, index) => (
              <div
                key={index}
                className="whitespace-pre-wrap text-gray-300 leading-relaxed"
              >
                {log}
              </div>
            ))}

            {status === 'BUILDING' && (
              <div className="flex items-center gap-2 mt-2 text-green-400">
                <span className="animate-pulse">▮</span>
                <span className="animate-pulse">Processing...</span>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Terminal Footer */}
      {status === 'DONE' && (
        <div className="px-4 py-3 bg-gray-900 border-t border-gray-800">
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono text-gray-500">
              Process completed with exit code 0
            </span>
            <button
              onClick={() => window.location.reload()}
              className="px-3 py-1 text-xs font-mono bg-primary-600 text-white rounded hover:bg-primary-700 transition-colors"
            >
              Start New
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
