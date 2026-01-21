import { create } from 'zustand';

// 1. Define the Shape of your "Glass Box"
export type BlueprintNode = {
  id: string;
  label: string;
  type: 'frontend' | 'backend' | 'database';
  status: 'pending' | 'approved' | 'rejected';
};

export type BlueprintPlan = {
  nodes: BlueprintNode[];
  database_changes: string[]; // e.g., "+ TABLE users"
  risk_audit: {
    status: 'SAFE' | 'WARNING' | 'CRITICAL';
    risks: string[];
  };
  cost_estimate: number;
};

type BlueprintState = {
  // Data
  plan: BlueprintPlan | null;
  chatHistory: { role: 'user' | 'ai'; content: string }[];
  terminalLogs: string[];

  // Metadata
  status: 'IDLE' | 'PLANNING' | 'NEGOTIATING' | 'BUILDING' | 'DONE';
  isConnected: boolean;

  // Actions
  setPlan: (plan: Partial<BlueprintPlan> | null) => void;
  addMessage: (role: 'user' | 'ai', content: string) => void;
  addTerminalLog: (log: string) => void;
  clearTerminalLogs: () => void;
  setStatus: (status: BlueprintState['status']) => void;
  setConnection: (status: boolean) => void;
  reset: () => void;
};

// 2. Create the Store
export const useBlueprintStore = create<BlueprintState>((set) => ({
  plan: null,
  chatHistory: [],
  terminalLogs: [],
  status: 'IDLE',
  isConnected: false,

  setPlan: (newPlan) =>
    set((state) => ({
      plan: newPlan
        ? (state.plan ? { ...state.plan, ...newPlan } : newPlan as BlueprintPlan)
        : null
    })),

  addMessage: (role, content) =>
    set((state) => ({
      chatHistory: [...state.chatHistory, { role, content }]
    })),

  addTerminalLog: (log) =>
    set((state) => ({
      terminalLogs: [...state.terminalLogs, log]
    })),

  clearTerminalLogs: () => set({ terminalLogs: [] }),

  setStatus: (status) => set({ status }),

  setConnection: (isConnected) => set({ isConnected }),

  reset: () => set({
    plan: null,
    chatHistory: [],
    terminalLogs: [],
    status: 'IDLE'
  }),
}));
