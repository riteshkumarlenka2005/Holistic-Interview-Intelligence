import { forwardRef, type ImgHTMLAttributes, useEffect, useState } from 'react'
import './image.css'
import { cn } from '@/lib/utils';

const FALLBACK_IMAGE_URL = "/placeholder.svg";

export type ImageProps = ImgHTMLAttributes<HTMLImageElement> & {
  fittingType?: 'fill' | 'fit';
  originWidth?: number;
  originHeight?: number;
  focalPointX?: number;
  focalPointY?: number;
}

export const Image = forwardRef<HTMLImageElement, ImageProps>(
  ({ src, fittingType = 'fill', originWidth, originHeight, className, style, ...props }, ref) => {
    const [imgSrc, setImgSrc] = useState<string | undefined>(src);
    const [hasError, setHasError] = useState(false);

    useEffect(() => {
      if (src !== imgSrc) {
        setImgSrc(src);
        setHasError(false);
      }
    }, [src]);

    const handleError = () => {
      if (!hasError) {
        setHasError(true);
        setImgSrc(FALLBACK_IMAGE_URL);
      }
    };

    if (!src) {
      return <div data-empty-image ref={ref as any} {...props} />;
    }

    // Calculate aspect ratio for wrapper
    const aspectRatio = originWidth && originHeight ? `${originWidth} / ${originHeight}` : undefined;
    const defaultWidth = originWidth ? `${originWidth}px` : undefined;

    return (
      <span
        className={cn('inline-block relative', className)}
        style={{
          '--img-aspect-ratio': aspectRatio,
          '--img-default-width': defaultWidth,
          ...style,
        } as React.CSSProperties}
      >
        <img
          ref={ref}
          src={imgSrc}
          className={cn(
            'w-full h-full inset-0 absolute',
            fittingType === 'fit' ? 'object-contain' : 'object-cover'
          )}
          onError={handleError}
          data-error-image={hasError}
          {...props}
        />
      </span>
    );
  }
);
Image.displayName = 'Image';
