/**
 * WebRTC Client
 * Complete client for connecting to signaling server
 */

import { createPeerConnection, webRTCConfig, PeerConnectionOptions } from './webrtc-config';

export type SignalingMessage = {
    type: 'join' | 'offer' | 'answer' | 'ice-candidate' | 'leave' | 'peer-joined' | 'peer-left';
    roomId?: string;
    clientId?: string;
    targetId?: string;
    peerId?: string;
    sdp?: RTCSessionDescriptionInit;
    candidate?: RTCIceCandidateInit;
};

export interface WebRTCClientEvents {
    onConnected?: () => void;
    onDisconnected?: () => void;
    onPeerJoined?: (peerId: string) => void;
    onPeerLeft?: (peerId: string) => void;
    onRemoteStream?: (stream: MediaStream, peerId: string) => void;
    onError?: (error: Error) => void;
}

export class WebRTCClient {
    private socket: WebSocket | null = null;
    private peerConnections: Map<string, RTCPeerConnection> = new Map();
    private localStream: MediaStream | null = null;
    private roomId: string | null = null;
    private clientId: string;
    private events: WebRTCClientEvents;
    private signalingUrl: string;

    constructor(signalingUrl: string, events: WebRTCClientEvents = {}) {
        this.signalingUrl = signalingUrl;
        this.clientId = this.generateClientId();
        this.events = events;
    }

    private generateClientId(): string {
        return 'client_' + Math.random().toString(36).substr(2, 9);
    }

    async connect(): Promise<void> {
        return new Promise((resolve, reject) => {
            try {
                this.socket = new WebSocket(this.signalingUrl);

                this.socket.onopen = () => {
                    console.log('Connected to signaling server');
                    this.events.onConnected?.();
                    resolve();
                };

                this.socket.onclose = () => {
                    console.log('Disconnected from signaling server');
                    this.events.onDisconnected?.();
                };

                this.socket.onerror = (error) => {
                    console.error('WebSocket error:', error);
                    this.events.onError?.(new Error('WebSocket connection failed'));
                    reject(error);
                };

                this.socket.onmessage = (event) => {
                    this.handleSignalingMessage(JSON.parse(event.data));
                };
            } catch (error) {
                reject(error);
            }
        });
    }

    async joinRoom(roomId: string, stream?: MediaStream): Promise<void> {
        this.roomId = roomId;
        this.localStream = stream || null;

        this.sendSignalingMessage({
            type: 'join',
            roomId,
            clientId: this.clientId
        });
    }

    private async handleSignalingMessage(message: SignalingMessage): Promise<void> {
        switch (message.type) {
            case 'peer-joined':
                if (message.peerId) {
                    await this.handlePeerJoined(message.peerId);
                }
                break;

            case 'peer-left':
                if (message.peerId) {
                    this.handlePeerLeft(message.peerId);
                }
                break;

            case 'offer':
                if (message.sdp && message.clientId) {
                    await this.handleOffer(message.sdp, message.clientId);
                }
                break;

            case 'answer':
                if (message.sdp && message.clientId) {
                    await this.handleAnswer(message.sdp, message.clientId);
                }
                break;

            case 'ice-candidate':
                if (message.candidate && message.clientId) {
                    await this.handleIceCandidate(message.candidate, message.clientId);
                }
                break;
        }
    }

    private async handlePeerJoined(peerId: string): Promise<void> {
        console.log('Peer joined:', peerId);
        this.events.onPeerJoined?.(peerId);

        // Create offer for new peer
        const pc = this.createPeerConnection(peerId);
        this.peerConnections.set(peerId, pc);

        // Add local tracks
        if (this.localStream) {
            this.localStream.getTracks().forEach(track => {
                pc.addTrack(track, this.localStream!);
            });
        }

        // Create and send offer
        const offer = await pc.createOffer();
        await pc.setLocalDescription(offer);

        this.sendSignalingMessage({
            type: 'offer',
            targetId: peerId,
            clientId: this.clientId,
            sdp: offer
        });
    }

    private handlePeerLeft(peerId: string): void {
        console.log('Peer left:', peerId);
        this.events.onPeerLeft?.(peerId);

        const pc = this.peerConnections.get(peerId);
        if (pc) {
            pc.close();
            this.peerConnections.delete(peerId);
        }
    }

    private async handleOffer(sdp: RTCSessionDescriptionInit, peerId: string): Promise<void> {
        let pc = this.peerConnections.get(peerId);

        if (!pc) {
            pc = this.createPeerConnection(peerId);
            this.peerConnections.set(peerId, pc);
        }

        // Add local tracks
        if (this.localStream) {
            this.localStream.getTracks().forEach(track => {
                pc!.addTrack(track, this.localStream!);
            });
        }

        await pc.setRemoteDescription(new RTCSessionDescription(sdp));

        const answer = await pc.createAnswer();
        await pc.setLocalDescription(answer);

        this.sendSignalingMessage({
            type: 'answer',
            targetId: peerId,
            clientId: this.clientId,
            sdp: answer
        });
    }

    private async handleAnswer(sdp: RTCSessionDescriptionInit, peerId: string): Promise<void> {
        const pc = this.peerConnections.get(peerId);
        if (pc) {
            await pc.setRemoteDescription(new RTCSessionDescription(sdp));
        }
    }

    private async handleIceCandidate(candidate: RTCIceCandidateInit, peerId: string): Promise<void> {
        const pc = this.peerConnections.get(peerId);
        if (pc) {
            await pc.addIceCandidate(new RTCIceCandidate(candidate));
        }
    }

    private createPeerConnection(peerId: string): RTCPeerConnection {
        const options: PeerConnectionOptions = {
            onTrack: (event) => {
                if (event.streams[0]) {
                    this.events.onRemoteStream?.(event.streams[0], peerId);
                }
            },
            onIceCandidate: (candidate) => {
                this.sendSignalingMessage({
                    type: 'ice-candidate',
                    targetId: peerId,
                    clientId: this.clientId,
                    candidate: candidate.toJSON()
                });
            },
            onConnectionStateChange: (state) => {
                console.log(`Connection state with ${peerId}:`, state);
            }
        };

        return createPeerConnection(options);
    }

    private sendSignalingMessage(message: SignalingMessage): void {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify(message));
        }
    }

    leaveRoom(): void {
        if (this.roomId) {
            this.sendSignalingMessage({
                type: 'leave',
                roomId: this.roomId,
                clientId: this.clientId
            });
        }

        // Close all peer connections
        this.peerConnections.forEach((pc) => pc.close());
        this.peerConnections.clear();

        this.roomId = null;
    }

    disconnect(): void {
        this.leaveRoom();

        if (this.socket) {
            this.socket.close();
            this.socket = null;
        }
    }

    getClientId(): string {
        return this.clientId;
    }

    isConnected(): boolean {
        return this.socket?.readyState === WebSocket.OPEN;
    }
}

export default WebRTCClient;
