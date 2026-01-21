'use client';

import { ChatInterface } from '@/components/Blueprint/ChatInterface';
import { BlueprintView } from '@/components/Blueprint/BlueprintView';
import Header from '@/components/Header';

export default function AIAgentPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Header />

      <div className="h-[calc(100vh-73px)] flex">
        {/* Left Side: Chat */}
        <div className="w-1/2 border-r border-gray-200">
          <ChatInterface />
        </div>

        {/* Right Side: Blueprint */}
        <div className="w-1/2">
          <BlueprintView />
        </div>
      </div>
    </div>
  );
}
