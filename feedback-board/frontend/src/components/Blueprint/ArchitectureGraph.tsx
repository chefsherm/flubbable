'use client';

import type { BlueprintNode } from '@/store/blueprintStore';

interface Props {
  nodes: BlueprintNode[];
}

export function ArchitectureGraph({ nodes }: Props) {
  // Group nodes by type
  const nodesByType = {
    frontend: nodes.filter(n => n.type === 'frontend'),
    backend: nodes.filter(n => n.type === 'backend'),
    database: nodes.filter(n => n.type === 'database'),
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'frontend':
        return 'bg-blue-900/40 border-blue-500 text-blue-300';
      case 'backend':
        return 'bg-purple-900/40 border-purple-500 text-purple-300';
      case 'database':
        return 'bg-green-900/40 border-green-500 text-green-300';
      default:
        return 'bg-gray-900/40 border-gray-500 text-gray-300';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'frontend':
        return '🎨';
      case 'backend':
        return '⚙️';
      case 'database':
        return '💾';
      default:
        return '📦';
    }
  };

  return (
    <div className="space-y-4">
      {/* Frontend Layer */}
      {nodesByType.frontend.length > 0 && (
        <div>
          <div className="text-xs font-semibold text-gray-500 mb-2 uppercase tracking-wide">
            Frontend Layer
          </div>
          <div className="grid grid-cols-2 gap-2">
            {nodesByType.frontend.map((node) => (
              <div
                key={node.id}
                className={`p-3 rounded-lg border ${getTypeColor(node.type)}`}
              >
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-lg">{getTypeIcon(node.type)}</span>
                  <span className="font-semibold text-sm">{node.id}</span>
                </div>
                <p className="text-xs text-gray-400">{node.label}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Connection Indicator */}
      {nodesByType.frontend.length > 0 && nodesByType.backend.length > 0 && (
        <div className="flex justify-center">
          <div className="w-px h-8 bg-gradient-to-b from-gray-600 to-transparent"></div>
        </div>
      )}

      {/* Backend Layer */}
      {nodesByType.backend.length > 0 && (
        <div>
          <div className="text-xs font-semibold text-gray-500 mb-2 uppercase tracking-wide">
            Backend Layer
          </div>
          <div className="grid grid-cols-2 gap-2">
            {nodesByType.backend.map((node) => (
              <div
                key={node.id}
                className={`p-3 rounded-lg border ${getTypeColor(node.type)}`}
              >
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-lg">{getTypeIcon(node.type)}</span>
                  <span className="font-semibold text-sm">{node.id}</span>
                </div>
                <p className="text-xs text-gray-400">{node.label}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Connection Indicator */}
      {nodesByType.backend.length > 0 && nodesByType.database.length > 0 && (
        <div className="flex justify-center">
          <div className="w-px h-8 bg-gradient-to-b from-gray-600 to-transparent"></div>
        </div>
      )}

      {/* Database Layer */}
      {nodesByType.database.length > 0 && (
        <div>
          <div className="text-xs font-semibold text-gray-500 mb-2 uppercase tracking-wide">
            Database Layer
          </div>
          <div className="grid grid-cols-2 gap-2">
            {nodesByType.database.map((node) => (
              <div
                key={node.id}
                className={`p-3 rounded-lg border ${getTypeColor(node.type)}`}
              >
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-lg">{getTypeIcon(node.type)}</span>
                  <span className="font-semibold text-sm">{node.id}</span>
                </div>
                <p className="text-xs text-gray-400">{node.label}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Summary */}
      <div className="mt-4 pt-4 border-t border-gray-800">
        <div className="flex justify-between text-xs text-gray-500">
          <span>Total Components:</span>
          <span className="font-semibold text-white">{nodes.length}</span>
        </div>
      </div>
    </div>
  );
}
