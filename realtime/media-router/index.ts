/**
 * Media Router Module
 * Exports all media capture and WebRTC utilities
 */

export {
    webRTCConfig,
    mediaConstraints,
    createPeerConnection,
    PeerConnectionOptions
} from './webrtc-config';

export {
    MediaCapture,
    AudioAnalyzer,
    RecordingOptions,
    CaptureConfig
} from './media-capture';

export {
    WebRTCClient,
    SignalingMessage,
    WebRTCClientEvents
} from './webrtc-client';
