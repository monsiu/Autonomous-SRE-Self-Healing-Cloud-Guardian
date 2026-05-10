import { useEffect, useRef, useState } from 'react';

export function useWebSocket<T>(url: string) {
  const [data, setData] = useState<T | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const shouldReconnectRef = useRef(true);

  useEffect(() => {
    shouldReconnectRef.current = true;

    const connect = () => {
      if (!shouldReconnectRef.current) return;

      try {
        console.log(`Connecting to ${url}...`);
        const ws = new WebSocket(url);
        wsRef.current = ws;

        ws.onopen = () => {
          if (!shouldReconnectRef.current) {
            ws.close();
            return;
          }
          console.log(`✅ Connected to ${url}`);
          setIsConnected(true);
        };

        ws.onmessage = (event) => {
          if (!shouldReconnectRef.current) return;
          try {
            const parsed = JSON.parse(event.data);
            if (parsed.type !== 'pong') {
              setData(parsed);
            }
          } catch (error) {
            console.error('Parse error:', error);
          }
        };

        ws.onerror = (error) => {
          console.error(`WebSocket error on ${url}:`, error);
        };

        ws.onclose = (event) => {
          if (!shouldReconnectRef.current) return;
          
          console.log(`Disconnected from ${url} (code: ${event.code})`);
          setIsConnected(false);
          
          // Reconnect after 5 seconds
          reconnectTimeoutRef.current = setTimeout(() => {
            if (shouldReconnectRef.current) {
              connect();
            }
          }, 5000);
        };
      } catch (error) {
        console.error(`Failed to connect to ${url}:`, error);
        setIsConnected(false);
      }
    };

    connect();

    // Cleanup on unmount
    return () => {
      shouldReconnectRef.current = false;
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
        reconnectTimeoutRef.current = null;
      }
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  }, [url]);

  return { data, isConnected };
}
