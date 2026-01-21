'use client';

interface Props {
  changes: string[];
}

export function DatabaseDiff({ changes }: Props) {
  const getChangeType = (change: string): 'add' | 'modify' | 'delete' => {
    if (change.startsWith('+')) return 'add';
    if (change.startsWith('-')) return 'delete';
    return 'modify';
  };

  const getChangeColor = (type: 'add' | 'modify' | 'delete') => {
    switch (type) {
      case 'add':
        return 'bg-green-900/20 border-green-600 text-green-400';
      case 'delete':
        return 'bg-red-900/20 border-red-600 text-red-400';
      case 'modify':
        return 'bg-yellow-900/20 border-yellow-600 text-yellow-400';
    }
  };

  const getChangeIcon = (type: 'add' | 'modify' | 'delete') => {
    switch (type) {
      case 'add':
        return '+';
      case 'delete':
        return '-';
      case 'modify':
        return '~';
    }
  };

  return (
    <div className="space-y-2">
      {changes.map((change, index) => {
        const type = getChangeType(change);
        const colorClass = getChangeColor(type);
        const icon = getChangeIcon(type);
        // Remove the +/- prefix if present
        const cleanChange = change.replace(/^[+\-~]\s*/, '');

        return (
          <div
            key={index}
            className={`p-3 rounded-lg border font-mono text-sm ${colorClass}`}
          >
            <div className="flex items-start gap-2">
              <span className="font-bold">{icon}</span>
              <span>{cleanChange}</span>
            </div>
          </div>
        );
      })}

      {changes.length === 0 && (
        <div className="p-4 rounded-lg border border-gray-700 bg-gray-800/50 text-center">
          <p className="text-sm text-gray-400">No database changes required</p>
        </div>
      )}
    </div>
  );
}
