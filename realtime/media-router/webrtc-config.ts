/**
 * WebRTC Configuration
 */

export const webRTCConfig: RTCConfiguration = {
    iceServers: [
        { urls: 'stun:stun.l.google.com:19302' },
        { urls: 'stun:stun1.l.google.com:19302' },
        // Add TURN servers for production
        // {
        //   urls: 'turn:your-turn-server.com:3478',
        //   username: 'username',
        //   credential: 'password'
        // }
    ],
    iceCandidatePoolSize: 10,
};

export const mediaConstraints: MediaStreamConstraints = {
    video: {
        width: { ideal: 1280 },
        height: { ideal: 720 },
        frameRate: { ideal: 30 },
        facingMode: 'user'
    },
    audio: {
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: true
    }
};

export interface PeerConnectionOptions {
    onTrack?: (event: RTCTrackEvent) => void;
    onIceCandidate?: (candidate: RTCIceCandidate) => void;
    onConnectionStateChange?: (state: RTCPeerConnectionState) => void;
}

export function createPeerConnection(options: PeerConnectionOptions): RTCPeerConnection {
    const pc = new RTCPeerConnection(webRTCConfig);

    if (options.onTrack) {
        pc.ontrack = options.onTrack;
    }

    if (options.onIceCandidate) {
        pc.onicecandidate = (event) => {
            if (event.candidate && options.onIceCandidate) {
                options.onIceCandidate(event.candidate);
            }
        };
    }

    if (options.onConnectionStateChange) {
        pc.onconnectionstatechange = () => {
            options.onConnectionStateChange!(pc.connectionState);
        };
    }

    return pc;
}
