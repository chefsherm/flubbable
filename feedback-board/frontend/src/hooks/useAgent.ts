import { useEffect, useRef, useCallback } from 'react';
import { useBlueprintStore } from '@/store/blueprintStore';

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws/agent';

export function useAgent() {
  const socketRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>();
  const {
    setConnection,
    setPlan,
    addTerminalLog,
    setStatus,
    addMessage
  } = useBlueprintStore();

  const connect = useCallback(() => {
    try {
      const ws = new WebSocket(WS_URL);
      socketRef.current = ws;

      ws.onopen = () => {
        console.log('🔌 WebSocket connected');
        setConnection(true);
      };

      ws.onclose = () => {
        console.log('🔌 WebSocket disconnected');
        setConnection(false);

        // Attempt to reconnect after 3 seconds
        reconnectTimeoutRef.current = setTimeout(() => {
          console.log('🔄 Attempting to reconnect...');
          connect();
        }, 3000);
      };

      ws.onerror = (error) => {
        console.error('❌ WebSocket error:', error);
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log('📨 Received:', data.type);

          switch (data.type) {
            case 'BLUEPRINT_GENERATED':
              setPlan(data.payload);
              setStatus('NEGOTIATING');
              addMessage('ai', 'Blueprint generated! Review and approve to continue.');
              break;

            case 'BUILD_STARTED':
              setStatus('BUILDING');
              addTerminalLog('🚀 Build process started...');
              break;

            case 'TERMINAL_LOG':
              addTerminalLog(data.payload.message || data.payload);
              break;

            case 'BUILD_COMPLETE':
              setStatus('DONE');
              addTerminalLog('✅ Build completed successfully!');
              addMessage('ai', 'Feature implemented successfully!');
              break;

            case 'CODE_UPDATED':
              addTerminalLog('📝 Code generated:');
              addTerminalLog(data.payload);
              break;

            case 'ERROR':
              addTerminalLog(`❌ Error: ${data.payload.message}`);
              addMessage('ai', `Error: ${data.payload.message}`);
              break;

            case 'PONG':
              // Keepalive response
              break;

            default:
              console.warn('Unknown message type:', data.type);
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };
    } catch (error) {
      console.error('Error creating WebSocket:', error);
    }
  }, [setConnection, setPlan, addTerminalLog, setStatus, addMessage]);

  useEffect(() => {
    connect();

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (socketRef.current) {
        socketRef.current.close();
      }
    };
  }, [connect]);

  // Send a plan generation request
  const requestPlan = useCallback((text: string) => {
    if (!socketRef.current || socketRef.current.readyState !== WebSocket.OPEN) {
      console.error('WebSocket not connected');
      return;
    }

    socketRef.current.send(JSON.stringify({
      type: "GENERATE_PLAN",
      payload: { message: text }
    }));

    setStatus('PLANNING');
    addMessage('user', text);
    addMessage('ai', 'Analyzing your request and generating blueprint...');
  }, [setStatus, addMessage]);

  // Send approval and trigger build
  const approveBuild = useCallback((currentPlan: any) => {
    if (!socketRef.current || socketRef.current.readyState !== WebSocket.OPEN) {
      console.error('WebSocket not connected');
      return;
    }

    socketRef.current.send(JSON.stringify({
      type: "APPROVE_PLAN",
      payload: { plan: currentPlan }
    }));

    addMessage('user', 'Approved! Starting build...');
  }, [addMessage]);

  // Send ping to keep connection alive
  const sendPing = useCallback(() => {
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify({ type: "PING" }));
    }
  }, []);

  // Ping every 30 seconds to keep connection alive
  useEffect(() => {
    const interval = setInterval(sendPing, 30000);
    return () => clearInterval(interval);
  }, [sendPing]);

  return {
    requestPlan,
    approveBuild,
    isConnected: socketRef.current?.readyState === WebSocket.OPEN
  };
}
