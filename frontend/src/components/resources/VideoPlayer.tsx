/**
 * VideoPlayer Component
 * Immersive video experience with embedded player or preview
 */
import { useState } from 'react';
import { motion } from 'framer-motion';
import {
    Play, ExternalLink, Clock, Volume2,
    Maximize2, CheckCircle2
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Image } from '@/components/ui/image';
import { Progress } from '@/components/ui/progress';

interface VideoPlayerProps {
    videoUrl: string;
    thumbnailUrl?: string;
    title?: string;
    duration?: string;
    progress?: number;
    onProgressUpdate?: (progress: number) => void;
}

// Extract video ID from various URL formats
function extractVideoId(url: string): { platform: 'youtube' | 'vimeo' | 'other'; id: string | null } {
    // YouTube
    const youtubePatterns = [
        /(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)/,
        /youtube\.com\/v\/([^&\n?#]+)/
    ];

    for (const pattern of youtubePatterns) {
        const match = url.match(pattern);
        if (match) return { platform: 'youtube', id: match[1] };
    }

    // Vimeo
    const vimeoPattern = /vimeo\.com\/(\d+)/;
    const vimeoMatch = url.match(vimeoPattern);
    if (vimeoMatch) return { platform: 'vimeo', id: vimeoMatch[1] };

    return { platform: 'other', id: null };
}

export function VideoPlayer({
    videoUrl,
    thumbnailUrl,
    title = 'Video Content',
    duration = '15 min',
    progress = 0,
    onProgressUpdate
}: VideoPlayerProps) {
    const [isPlaying, setIsPlaying] = useState(false);
    const videoInfo = extractVideoId(videoUrl);

    const canEmbed = videoInfo.platform !== 'other' && videoInfo.id;

    const getEmbedUrl = () => {
        if (videoInfo.platform === 'youtube' && videoInfo.id) {
            return `https://www.youtube-nocookie.com/embed/${videoInfo.id}?autoplay=1&rel=0`;
        }
        if (videoInfo.platform === 'vimeo' && videoInfo.id) {
            return `https://player.vimeo.com/video/${videoInfo.id}?autoplay=1`;
        }
        return null;
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="bg-white border border-lavender-200 rounded-2xl overflow-hidden shadow-sm"
        >
            {/* Video Container */}
            <div className="relative aspect-video bg-slate-900">
                {isPlaying && canEmbed ? (
                    // Embedded Player
                    <iframe
                        src={getEmbedUrl() || ''}
                        title={title}
                        className="absolute inset-0 w-full h-full"
                        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                        allowFullScreen
                    />
                ) : (
                    // Preview State
                    <>
                        {/* Thumbnail or Gradient Background */}
                        {thumbnailUrl ? (
                            <Image
                                src={thumbnailUrl}
                                alt={title}
                                width={1280}
                                className="absolute inset-0 w-full h-full object-cover"
                            />
                        ) : (
                            <div className="absolute inset-0 bg-gradient-to-br from-slate-800 to-slate-900" />
                        )}

                        {/* Overlay */}
                        <div className="absolute inset-0 bg-black/40 flex items-center justify-center">
                            {/* Play Button */}
                            <motion.button
                                onClick={() => canEmbed ? setIsPlaying(true) : window.open(videoUrl, '_blank')}
                                whileHover={{ scale: 1.05 }}
                                whileTap={{ scale: 0.95 }}
                                className="group relative w-20 h-20 lg:w-24 lg:h-24 rounded-full 
                           bg-white/95 shadow-2xl flex items-center justify-center
                           hover:bg-white transition-colors"
                            >
                                <Play className="w-8 h-8 lg:w-10 lg:h-10 text-primary ml-1" />

                                {/* Pulse animation */}
                                <span className="absolute inset-0 rounded-full bg-white/30 animate-ping" />
                            </motion.button>
                        </div>

                        {/* Duration Badge */}
                        <div className="absolute top-4 right-4 flex items-center gap-2 px-3 py-1.5 
                            bg-black/60 rounded-lg backdrop-blur-sm">
                            <Clock className="w-4 h-4 text-white/80" />
                            <span className="text-sm font-medium text-white">{duration}</span>
                        </div>

                        {/* Title Overlay */}
                        <div className="absolute bottom-0 left-0 right-0 p-6 
                            bg-gradient-to-t from-black/80 to-transparent">
                            <h3 className="font-heading text-xl lg:text-2xl font-bold text-white mb-2">
                                {title}
                            </h3>
                            <p className="text-white/70 text-sm">
                                {canEmbed ? 'Click to play video' : 'Opens in new tab'}
                            </p>
                        </div>
                    </>
                )}
            </div>

            {/* Video Controls Bar */}
            <div className="px-6 py-4 bg-lavender-50/50 border-t border-lavender-100">
                <div className="flex items-center justify-between gap-4">
                    {/* Progress */}
                    <div className="flex-1">
                        {progress > 0 ? (
                            <div className="space-y-1">
                                <div className="flex items-center justify-between text-xs">
                                    <span className="text-foreground/60">Your progress</span>
                                    <span className="font-medium text-primary">{progress}%</span>
                                </div>
                                <Progress value={progress} className="h-1.5" />
                            </div>
                        ) : (
                            <div className="flex items-center gap-2 text-sm text-foreground/60">
                                <Volume2 className="w-4 h-4" />
                                <span>Ready to watch</span>
                            </div>
                        )}
                    </div>

                    {/* Actions */}
                    <div className="flex items-center gap-2">
                        {!isPlaying && (
                            <Button
                                onClick={() => canEmbed ? setIsPlaying(true) : window.open(videoUrl, '_blank')}
                                className="bg-primary text-white hover:bg-primary/90 rounded-lg h-9 px-4"
                            >
                                <Play className="w-4 h-4 mr-1.5" />
                                {canEmbed ? 'Play Video' : 'Watch Now'}
                            </Button>
                        )}

                        {isPlaying && (
                            <Button
                                onClick={() => setIsPlaying(false)}
                                variant="outline"
                                className="border-lavender-200 text-foreground/70 hover:bg-lavender-100 rounded-lg h-9 px-4"
                            >
                                Close Player
                            </Button>
                        )}

                        <a
                            href={videoUrl}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="p-2 rounded-lg border border-lavender-200 text-foreground/50 
                         hover:bg-lavender-100 hover:text-foreground transition-colors"
                            title="Open in new tab"
                        >
                            <ExternalLink className="w-4 h-4" />
                        </a>
                    </div>
                </div>
            </div>
        </motion.div>
    );
}

export default VideoPlayer;
