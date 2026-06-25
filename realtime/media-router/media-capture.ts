/**
 * Media Capture Utilities
 * Handles video/audio capture for interview analysis
 */

import { webRTCConfig, mediaConstraints } from './webrtc-config';

export interface RecordingOptions {
    mimeType?: string;
    videoBitsPerSecond?: number;
    audioBitsPerSecond?: number;
}

export interface CaptureConfig {
    captureVideo: boolean;
    captureAudio: boolean;
    recordLocally: boolean;
    snapshotInterval?: number; // ms, for periodic frame capture
}

export class MediaCapture {
    private stream: MediaStream | null = null;
    private recorder: MediaRecorder | null = null;
    private recordedChunks: Blob[] = [];
    private snapshotCanvas: HTMLCanvasElement | null = null;
    private snapshotInterval: number | null = null;
    private isRecording: boolean = false;

    async startCapture(config: CaptureConfig = {
        captureVideo: true,
        captureAudio: true,
        recordLocally: false
    }): Promise<MediaStream> {
        const constraints: MediaStreamConstraints = {
            video: config.captureVideo ? mediaConstraints.video : false,
            audio: config.captureAudio ? mediaConstraints.audio : false
        };

        try {
            this.stream = await navigator.mediaDevices.getUserMedia(constraints);

            if (config.recordLocally) {
                this.initializeRecorder();
            }

            if (config.snapshotInterval && config.captureVideo) {
                this.startSnapshotCapture(config.snapshotInterval);
            }

            return this.stream;
        } catch (error) {
            console.error('Failed to capture media:', error);
            throw error;
        }
    }

    private initializeRecorder(options?: RecordingOptions): void {
        if (!this.stream) return;

        const mimeType = options?.mimeType || 'video/webm;codecs=vp9,opus';

        if (!MediaRecorder.isTypeSupported(mimeType)) {
            console.warn(`${mimeType} not supported, falling back to default`);
        }

        this.recorder = new MediaRecorder(this.stream, {
            mimeType: MediaRecorder.isTypeSupported(mimeType) ? mimeType : 'video/webm',
            videoBitsPerSecond: options?.videoBitsPerSecond || 2500000,
            audioBitsPerSecond: options?.audioBitsPerSecond || 128000
        });

        this.recorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
                this.recordedChunks.push(event.data);
            }
        };
    }

    startRecording(): void {
        if (!this.recorder) {
            this.initializeRecorder();
        }

        if (this.recorder && !this.isRecording) {
            this.recordedChunks = [];
            this.recorder.start(1000); // Collect data every second
            this.isRecording = true;
        }
    }

    stopRecording(): Blob | null {
        if (this.recorder && this.isRecording) {
            this.recorder.stop();
            this.isRecording = false;

            return new Blob(this.recordedChunks, {
                type: this.recorder.mimeType
            });
        }
        return null;
    }

    private startSnapshotCapture(intervalMs: number): void {
        this.snapshotCanvas = document.createElement('canvas');

        const videoTrack = this.stream?.getVideoTracks()[0];
        if (!videoTrack) return;

        const settings = videoTrack.getSettings();
        this.snapshotCanvas.width = settings.width || 640;
        this.snapshotCanvas.height = settings.height || 480;

        this.snapshotInterval = window.setInterval(() => {
            const frame = this.captureFrame();
            if (frame) {
                // Emit frame for analysis (can be customized)
                window.dispatchEvent(new CustomEvent('frame-captured', {
                    detail: frame
                }));
            }
        }, intervalMs);
    }

    captureFrame(): ImageData | null {
        if (!this.stream || !this.snapshotCanvas) return null;

        const video = document.createElement('video');
        video.srcObject = this.stream;
        video.play();

        const ctx = this.snapshotCanvas.getContext('2d');
        if (!ctx) return null;

        ctx.drawImage(
            video,
            0, 0,
            this.snapshotCanvas.width,
            this.snapshotCanvas.height
        );

        return ctx.getImageData(
            0, 0,
            this.snapshotCanvas.width,
            this.snapshotCanvas.height
        );
    }

    captureFrameAsBlob(type: string = 'image/jpeg', quality: number = 0.8): Promise<Blob | null> {
        return new Promise((resolve) => {
            if (!this.stream) {
                resolve(null);
                return;
            }

            const video = document.createElement('video');
            video.srcObject = this.stream;
            video.onloadedmetadata = () => {
                video.play();

                const canvas = document.createElement('canvas');
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;

                const ctx = canvas.getContext('2d');
                if (ctx) {
                    ctx.drawImage(video, 0, 0);
                    canvas.toBlob((blob) => resolve(blob), type, quality);
                } else {
                    resolve(null);
                }
            };
        });
    }

    getStream(): MediaStream | null {
        return this.stream;
    }

    getAudioTrack(): MediaStreamTrack | undefined {
        return this.stream?.getAudioTracks()[0];
    }

    getVideoTrack(): MediaStreamTrack | undefined {
        return this.stream?.getVideoTracks()[0];
    }

    stopCapture(): void {
        // Stop recording
        if (this.isRecording) {
            this.stopRecording();
        }

        // Clear snapshot interval
        if (this.snapshotInterval) {
            clearInterval(this.snapshotInterval);
            this.snapshotInterval = null;
        }

        // Stop all tracks
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.stream = null;
        }

        this.recorder = null;
    }

    async getRecordingAsFile(filename: string = 'recording.webm'): Promise<File | null> {
        const blob = this.stopRecording();
        if (blob) {
            return new File([blob], filename, { type: blob.type });
        }
        return null;
    }
}

/**
 * AudioAnalyzer for real-time audio metrics
 */
export class AudioAnalyzer {
    private audioContext: AudioContext | null = null;
    private analyser: AnalyserNode | null = null;
    private dataArray: Uint8Array | null = null;

    initialize(stream: MediaStream): void {
        this.audioContext = new AudioContext();
        this.analyser = this.audioContext.createAnalyser();
        this.analyser.fftSize = 2048;

        const source = this.audioContext.createMediaStreamSource(stream);
        source.connect(this.analyser);

        this.dataArray = new Uint8Array(this.analyser.frequencyBinCount);
    }

    getAudioLevel(): number {
        if (!this.analyser || !this.dataArray) return 0;

        this.analyser.getByteFrequencyData(this.dataArray);

        let sum = 0;
        for (let i = 0; i < this.dataArray.length; i++) {
            sum += this.dataArray[i];
        }

        return sum / this.dataArray.length / 255; // Normalized 0-1
    }

    isSpeaking(threshold: number = 0.1): boolean {
        return this.getAudioLevel() > threshold;
    }

    getFrequencyData(): Uint8Array | null {
        if (!this.analyser || !this.dataArray) return null;
        this.analyser.getByteFrequencyData(this.dataArray);
        return this.dataArray;
    }

    dispose(): void {
        if (this.audioContext) {
            this.audioContext.close();
            this.audioContext = null;
        }
        this.analyser = null;
        this.dataArray = null;
    }
}

// Default export
export default MediaCapture;
