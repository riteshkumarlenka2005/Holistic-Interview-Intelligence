/**
 * WebSocket Handler for real-time communication
 */

export interface SignalingMessage {
    type: 'join' | 'offer' | 'answer' | 'ice-candidate' | 'leave';
    roomId?: string;
    clientId?: string;
    targetId?: string;
    payload?: RTCSessionDescriptionInit | RTCIceCandidateInit;
}

export class WebSocketClient {
    private ws: WebSocket | null = null;
    private reconnectAttempts = 0;
    private maxReconnectAttempts = 5;

    constructor(private url: string) { }

    connect(): Promise<void> {
        return new Promise((resolve, reject) => {
            this.ws = new WebSocket(this.url);

            this.ws.onopen = () => {
                this.reconnectAttempts = 0;
                resolve();
            };

            this.ws.onerror = (error) => {
                reject(error);
            };

            this.ws.onclose = () => {
                this.handleDisconnect();
            };
        });
    }

    send(message: SignalingMessage): void {
        if (this.ws?.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(message));
        }
    }

    onMessage(handler: (message: SignalingMessage) => void): void {
        if (this.ws) {
            this.ws.onmessage = (event) => {
                try {
                    const message = JSON.parse(event.data);
                    handler(message);
                } catch (error) {
                    console.error('Failed to parse message:', error);
                }
            };
        }
    }

    private handleDisconnect(): void {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            setTimeout(() => this.connect(), 1000 * this.reconnectAttempts);
        }
    }

    disconnect(): void {
        this.ws?.close();
        this.ws = null;
    }
}
