/**
 * FaceTrackingOverlay Component
 * 
 * SVG overlay that renders face detection rectangle and eye tracking indicators
 * on top of the video element. Shows gaze direction arrow and iris positions.
 */
import React from 'react';
import { motion } from 'framer-motion';
import { BehavioralMetrics } from '@/hooks/useBehavioralAnalysis';

interface FaceTrackingOverlayProps {
    metrics: BehavioralMetrics | null;
    videoWidth: number;
    videoHeight: number;
}

const FaceTrackingOverlay: React.FC<FaceTrackingOverlayProps> = ({
    metrics,
    videoWidth,
    videoHeight
}) => {
    if (!metrics || !metrics.face_detected) {
        return null;
    }

    const { face_box, left_iris_position, right_iris_position, gaze_direction, looking_at_camera, left_eye_box, right_eye_box } = metrics;

    // face_box is now normalized (0-1), convert to pixels
    // Format: [x, y, width, height] normalized
    const faceRect = face_box ? {
        x: face_box[0] * videoWidth,
        y: face_box[1] * videoHeight,
        width: face_box[2] * videoWidth,
        height: face_box[3] * videoHeight
    } : null;

    // Convert normalized iris positions to actual pixels
    const leftIris = left_iris_position ? {
        x: left_iris_position[0] * videoWidth,
        y: left_iris_position[1] * videoHeight
    } : null;

    const rightIris = right_iris_position ? {
        x: right_iris_position[0] * videoWidth,
        y: right_iris_position[1] * videoHeight
    } : null;

    // Convert normalized eye boxes to pixels for green eye rectangles
    const leftEyeRect = left_eye_box ? {
        x: left_eye_box[0] * videoWidth,
        y: left_eye_box[1] * videoHeight,
        width: left_eye_box[2] * videoWidth,
        height: left_eye_box[3] * videoHeight
    } : null;

    const rightEyeRect = right_eye_box ? {
        x: right_eye_box[0] * videoWidth,
        y: right_eye_box[1] * videoHeight,
        width: right_eye_box[2] * videoWidth,
        height: right_eye_box[3] * videoHeight
    } : null;

    // Get gaze arrow direction (raw, CSS will mirror)
    const getGazeArrow = () => {
        switch (gaze_direction) {
            case 'left': return { dx: -30, dy: 0 };
            case 'right': return { dx: 30, dy: 0 };
            case 'up': return { dx: 0, dy: -20 };
            case 'down': return { dx: 0, dy: 20 };
            default: return { dx: 0, dy: 0 };
        }
    };

    const arrow = getGazeArrow();
    const eyeCenter = leftIris && rightIris ? {
        x: (leftIris.x + rightIris.x) / 2,
        y: (leftIris.y + rightIris.y) / 2
    } : null;

    // Colors based on eye contact status
    const faceColor = looking_at_camera ? '#22c55e' : '#f97316'; // green or orange
    const eyeBoxColor = '#22c55e'; // Always bright green for eye boxes
    const pupilColor = '#ff0000'; // Bright red for pupils

    return (
        <svg
            className="absolute inset-0 pointer-events-none"
            width={videoWidth}
            height={videoHeight}
            viewBox={`0 0 ${videoWidth} ${videoHeight}`}
            style={{ transform: 'scaleX(-1)' }}  // Mirror to match video
        >
            {/* Face detection rectangle */}
            {faceRect && (
                <motion.rect
                    x={faceRect.x}
                    y={faceRect.y}
                    width={faceRect.width}
                    height={faceRect.height}
                    fill="none"
                    stroke={faceColor}
                    strokeWidth={3}
                    rx={8}
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.2 }}
                />
            )}

            {/* Corner markers for face box */}
            {faceRect && (
                <>
                    {/* Top-left corner */}
                    <path
                        d={`M ${faceRect.x} ${faceRect.y + 20} L ${faceRect.x} ${faceRect.y} L ${faceRect.x + 20} ${faceRect.y}`}
                        fill="none"
                        stroke={faceColor}
                        strokeWidth={4}
                        strokeLinecap="round"
                    />
                    {/* Top-right corner */}
                    <path
                        d={`M ${faceRect.x + faceRect.width - 20} ${faceRect.y} L ${faceRect.x + faceRect.width} ${faceRect.y} L ${faceRect.x + faceRect.width} ${faceRect.y + 20}`}
                        fill="none"
                        stroke={faceColor}
                        strokeWidth={4}
                        strokeLinecap="round"
                    />
                    {/* Bottom-left corner */}
                    <path
                        d={`M ${faceRect.x} ${faceRect.y + faceRect.height - 20} L ${faceRect.x} ${faceRect.y + faceRect.height} L ${faceRect.x + 20} ${faceRect.y + faceRect.height}`}
                        fill="none"
                        stroke={faceColor}
                        strokeWidth={4}
                        strokeLinecap="round"
                    />
                    {/* Bottom-right corner */}
                    <path
                        d={`M ${faceRect.x + faceRect.width - 20} ${faceRect.y + faceRect.height} L ${faceRect.x + faceRect.width} ${faceRect.y + faceRect.height} L ${faceRect.x + faceRect.width} ${faceRect.y + faceRect.height - 20}`}
                        fill="none"
                        stroke={faceColor}
                        strokeWidth={4}
                        strokeLinecap="round"
                    />
                </>
            )}

            {/* Left eye detection box - bright green rectangle */}
            {leftEyeRect && (
                <motion.rect
                    x={leftEyeRect.x}
                    y={leftEyeRect.y}
                    width={leftEyeRect.width}
                    height={leftEyeRect.height}
                    fill="none"
                    stroke={eyeBoxColor}
                    strokeWidth={2}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ duration: 0.2 }}
                />
            )}

            {/* Right eye detection box - bright green rectangle */}
            {rightEyeRect && (
                <motion.rect
                    x={rightEyeRect.x}
                    y={rightEyeRect.y}
                    width={rightEyeRect.width}
                    height={rightEyeRect.height}
                    fill="none"
                    stroke={eyeBoxColor}
                    strokeWidth={2}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ duration: 0.2 }}
                />
            )}

            {/* Left pupil indicator - red dot */}
            {leftIris && (
                <motion.circle
                    cx={leftIris.x}
                    cy={leftIris.y}
                    r={5}
                    fill={pupilColor}
                    stroke="white"
                    strokeWidth={1}
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ duration: 0.2 }}
                />
            )}

            {/* Right pupil indicator - red dot */}
            {rightIris && (
                <motion.circle
                    cx={rightIris.x}
                    cy={rightIris.y}
                    r={5}
                    fill={pupilColor}
                    stroke="white"
                    strokeWidth={1}
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ duration: 0.2 }}
                />
            )}

            {/* Gaze direction arrow (only when not looking at camera) */}
            {eyeCenter && !looking_at_camera && (arrow.dx !== 0 || arrow.dy !== 0) && (
                <motion.g
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ duration: 0.3 }}
                >
                    <line
                        x1={eyeCenter.x}
                        y1={eyeCenter.y}
                        x2={eyeCenter.x + arrow.dx}
                        y2={eyeCenter.y + arrow.dy}
                        stroke="#ef4444"
                        strokeWidth={3}
                        strokeLinecap="round"
                        markerEnd="url(#arrowhead)"
                    />
                    <defs>
                        <marker
                            id="arrowhead"
                            markerWidth="10"
                            markerHeight="7"
                            refX="9"
                            refY="3.5"
                            orient="auto"
                        >
                            <polygon
                                points="0 0, 10 3.5, 0 7"
                                fill="#ef4444"
                            />
                        </marker>
                    </defs>
                </motion.g>
            )}

            {/* Eye contact indicator at top-left of face */}
            {faceRect && (
                <g transform={`translate(${faceRect.x}, ${faceRect.y - 30})`}>
                    <rect
                        x={0}
                        y={0}
                        width={looking_at_camera ? 100 : 120}
                        height={24}
                        rx={12}
                        fill={looking_at_camera ? 'rgba(34, 197, 94, 0.9)' : 'rgba(249, 115, 22, 0.9)'}
                    />
                    <text
                        x={looking_at_camera ? 50 : 60}
                        y={16}
                        textAnchor="middle"
                        fill="white"
                        fontSize={11}
                        fontWeight="bold"
                    >
                        {looking_at_camera ? '👁 CENTER' : `⚠️ LOOKING ${gaze_direction.toUpperCase()}`}
                    </text>
                </g>
            )}
        </svg>
    );
};

export default FaceTrackingOverlay;
