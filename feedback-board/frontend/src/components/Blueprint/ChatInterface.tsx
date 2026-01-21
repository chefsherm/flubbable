'use client';

import { useState } from 'react';
import { useAgent } from '@/hooks/useAgent';
import { useBlueprintStore } from '@/store/blueprintStore';

export function ChatInterface() {
  const [input, setInput] = useState('');
  const { requestPlan } = useAgent();
  const { chatHistory, status, isConnected } = useBlueprintStore();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || status === 'PLANNING' || !isConnected) return;

    requestPlan(input.trim());
    setInput('');
  };

  return (
    <div className="flex flex-col h-full bg-gray-900">
      {/* Connection Status */}
      <div className="px-4 py-2 border-b border-gray-800 bg-black">
        <div className="flex items-center gap-2">
          <div
            className={`w-2 h-2 rounded-full ${
              isConnected ? 'bg-green-500' : 'bg-red-500'
            } ${isConnected ? 'animate-pulse' : ''}`}
          ></div>
          <span className="text-xs text-gray-400">
            {isConnected ? 'AI Connected' : 'Disconnected'}
          </span>
        </div>
      </div>

      {/* Chat History */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {chatHistory.length === 0 ? (
          <div className="text-center py-12">
            <div className="inline-block p-4 bg-gray-800 rounded-full mb-4">
              <svg
                className="w-8 h-8 text-gray-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
                />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-white mb-2">
              Start a conversation
            </h3>
            <p className="text-sm text-gray-400 max-w-sm mx-auto">
              Describe a feature you want to build and AI will generate a
              technical blueprint for review
            </p>
            <div className="mt-4 space-y-2">
              <button
                onClick={() =>
                  requestPlan('Create a user profile page with avatar upload')
                }
                className="block w-full max-w-sm mx-auto px-4 py-2 text-sm text-left bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors text-gray-300"
              >
                💡 User profile page with avatar
              </button>
              <button
                onClick={() =>
                  requestPlan('Add a search feature with filters and sorting')
                }
                className="block w-full max-w-sm mx-auto px-4 py-2 text-sm text-left bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors text-gray-300"
              >
                💡 Search with filters
              </button>
            </div>
          </div>
        ) : (
          chatHistory.map((message, index) => (
            <div
              key={index}
              className={`flex ${
                message.role === 'user' ? 'justify-end' : 'justify-start'
              }`}
            >
              <div
                className={`max-w-[80%] px-4 py-2 rounded-lg ${
                  message.role === 'user'
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-800 text-gray-200'
                }`}
              >
                <div className="flex items-start gap-2">
                  <span className="text-xs opacity-70">
                    {message.role === 'user' ? '👤' : '🤖'}
                  </span>
                  <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                </div>
              </div>
            </div>
          ))
        )}

        {status === 'PLANNING' && (
          <div className="flex justify-start">
            <div className="bg-gray-800 text-gray-200 px-4 py-2 rounded-lg">
              <div className="flex items-center gap-2">
                <div className="flex gap-1">
                  <div className="w-2 h-2 rounded-full bg-gray-500 animate-bounce"></div>
                  <div className="w-2 h-2 rounded-full bg-gray-500 animate-bounce delay-100"></div>
                  <div className="w-2 h-2 rounded-full bg-gray-500 animate-bounce delay-200"></div>
                </div>
                <span className="text-sm">AI is thinking...</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Input Form */}
      <div className="p-4 border-t border-gray-800 bg-black">
        <form onSubmit={handleSubmit} className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={
              isConnected
                ? 'Describe the feature you want to build...'
                : 'Connecting to AI...'
            }
            disabled={status === 'PLANNING' || !isConnected}
            className="flex-1 px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary-600 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed"
          />
          <button
            type="submit"
            disabled={!input.trim() || status === 'PLANNING' || !isConnected}
            className="px-6 py-2 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 disabled:bg-gray-700 disabled:cursor-not-allowed transition-colors"
          >
            {status === 'PLANNING' ? (
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
            ) : (
              'Send'
            )}
          </button>
        </form>
      </div>
    </div>
  );
}
