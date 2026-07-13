import * as React from 'react';

import { cn } from '@/lib/utils';

/**
 * IntensiCare brand mark.
 *
 * Geometry notes (see docs/... none — derived analytically, not traced from a
 * raster source): the icon is a ring enclosing two "squircle plus" outlines
 * (rounded-corner cross shapes, each hollowed out with an evenodd inner
 * cutout so the cross reads as a thick outlined "plus link" rather than a
 * solid tile). The two crosses are offset diagonally (blue centered
 * bottom-left, coral centered top-right) so their arms overlap in two spots,
 * mimicking two interlocked chain links:
 *   - the coral cross paints OVER the blue cross's top arm (normal paint
 *     order — coral is drawn after blue, so it wins by default), and
 *   - the coral cross paints UNDER the blue cross's right arm (a <mask>
 *     punches a hole in the coral layer exactly over that overlap region, so
 *     the blue arm drawn underneath shows through).
 * All numbers are in a 0-0-100-100 viewBox local to the icon.
 */

export const TAGLINE = 'Inovação que salva vidas.';

type LogoVariant = 'full' | 'icon' | 'wordmark';
type LogoTheme = 'dark' | 'light';

export interface LogoProps {
  /** Which piece of the mark to render. */
  variant?: LogoVariant;
  /** Surface the mark sits on. 'dark' (default) matches the v3 app shell. */
  theme?: LogoTheme;
  className?: string;
  /** Accessible name. Pass '' to mark the mark as purely decorative. */
  title?: string;
}

const ICON_VIEWBOX = '0 0 100 100';
const RING_R = 42;
const RING_STROKE_WIDTH = 8;

// Outer silhouette only (used for the solid/tiny-size fallback and as the
// base layer under the hollow evenodd cutout).
const CROSS_BLUE_OUTER =
  'M 38 36 L 46 36 Q 51 36 51 41 L 51 45 Q 51 49 55 49 L 59 49 Q 64 49 64 54 L 64 62 Q 64 67 59 67 L 55 67 Q 51 67 51 71 L 51 75 Q 51 80 46 80 L 38 80 Q 33 80 33 75 L 33 71 Q 33 67 29 67 L 25 67 Q 20 67 20 62 L 20 54 Q 20 49 25 49 L 29 49 Q 33 49 33 45 L 33 41 Q 33 36 38 36 Z';
// Outer + inner (evenodd) — the "vazado" plus-shaped frame.
const CROSS_BLUE_HOLLOW =
  CROSS_BLUE_OUTER +
  ' M 38 40 L 46 40 Q 47 40 47 41 L 47 45 Q 47 53 55 53 L 59 53 Q 60 53 60 54 L 60 62 Q 60 63 59 63 L 55 63 Q 47 63 47 71 L 47 75 Q 47 76 46 76 L 38 76 Q 37 76 37 75 L 37 71 Q 37 63 29 63 L 25 63 Q 24 63 24 62 L 24 54 Q 24 53 25 53 L 29 53 Q 37 53 37 45 L 37 41 Q 37 40 38 40 Z';

const CROSS_CORAL_OUTER =
  'M 54 20 L 62 20 Q 67 20 67 25 L 67 29 Q 67 33 71 33 L 75 33 Q 80 33 80 38 L 80 46 Q 80 51 75 51 L 71 51 Q 67 51 67 55 L 67 59 Q 67 64 62 64 L 54 64 Q 49 64 49 59 L 49 55 Q 49 51 45 51 L 41 51 Q 36 51 36 46 L 36 38 Q 36 33 41 33 L 45 33 Q 49 33 49 29 L 49 25 Q 49 20 54 20 Z';
const CROSS_CORAL_HOLLOW =
  CROSS_CORAL_OUTER +
  ' M 54 24 L 62 24 Q 63 24 63 25 L 63 29 Q 63 37 71 37 L 75 37 Q 76 37 76 38 L 76 46 Q 76 47 75 47 L 71 47 Q 63 47 63 55 L 63 59 Q 63 60 62 60 L 54 60 Q 53 60 53 59 L 53 55 Q 53 47 45 47 L 41 47 Q 40 47 40 46 L 40 38 Q 40 37 41 37 L 45 37 Q 53 37 53 29 L 53 25 Q 53 24 54 24 Z';

// Rect that exactly covers the blue cross's right arm — used as a mask
// cutout so the coral cross is hidden (i.e. renders "under") in that one
// overlap region, producing the interlocked-link illusion.
const WEAVE_MASK_RECT = { x: 51, y: 49, width: 13, height: 18 };

function IconMark({
  theme,
  hollow,
  maskId,
}: {
  theme: LogoTheme;
  hollow: boolean;
  maskId: string;
}) {
  // The crosses always keep their brand colors; only the ring swaps to the
  // lighter accent on dark surfaces for contrast.
  const ringColor = theme === 'dark' ? 'var(--brand-accent)' : 'var(--brand-primary)';
  const blueColor = 'var(--brand-primary)';
  const coralColor = 'var(--brand-coral)';
  const bluePath = hollow ? CROSS_BLUE_HOLLOW : CROSS_BLUE_OUTER;
  const coralPath = hollow ? CROSS_CORAL_HOLLOW : CROSS_CORAL_OUTER;

  return (
    <>
      <defs>
        <mask id={maskId} maskUnits="userSpaceOnUse">
          <rect x="0" y="0" width="100" height="100" fill="white" />
          <rect
            x={WEAVE_MASK_RECT.x}
            y={WEAVE_MASK_RECT.y}
            width={WEAVE_MASK_RECT.width}
            height={WEAVE_MASK_RECT.height}
            fill="black"
          />
        </mask>
      </defs>
      {/* Ring */}
      <circle cx="50" cy="50" r={RING_R} fill="none" stroke={ringColor} strokeWidth={RING_STROKE_WIDTH} />
      {/* Blue link — drawn first so coral can weave over/under it */}
      <path fillRule="evenodd" fill={blueColor} d={bluePath} />
      {/* Coral link — masked so it dips under the blue cross's right arm */}
      <g mask={`url(#${maskId})`}>
        <path fillRule="evenodd" fill={coralColor} d={coralPath} />
      </g>
    </>
  );
}

function Wordmark({ theme }: { theme: LogoTheme }) {
  const intensiColor = theme === 'dark' ? 'var(--brand-on-dark)' : 'var(--brand-primary)';
  const careColor = 'var(--brand-accent)';

  return (
    <text
      x="0"
      y="34"
      fontFamily='"Nunito", "Quicksand", ui-rounded, system-ui, sans-serif'
      fontWeight={800}
      fontSize="32"
      letterSpacing="-0.02em"
    >
      <tspan fill={intensiColor}>intensi</tspan>
      <tspan fill={careColor}>care</tspan>
    </text>
  );
}

/**
 * IntensiCare brand mark. Renders the icon, wordmark, or both, in either the
 * dark-surface (default, matches the v3 app shell) or light-surface palette.
 */
export function Logo({
  variant = 'full',
  theme = 'dark',
  className,
  title,
}: LogoProps) {
  const reactId = React.useId();
  const maskId = `brand-weave-${reactId}`;
  const labelledById = `brand-title-${reactId}`;
  const isDecorative = title === '';
  const accessibleLabel = title ?? 'IntensiCare';

  const a11yProps = isDecorative
    ? { 'aria-hidden': true as const }
    : { role: 'img' as const, 'aria-labelledby': labelledById };

  if (variant === 'icon') {
    return (
      <svg
        viewBox={ICON_VIEWBOX}
        className={cn('h-8 w-8', className)}
        xmlns="http://www.w3.org/2000/svg"
        {...a11yProps}
      >
        {!isDecorative && <title id={labelledById}>{accessibleLabel}</title>}
        <IconMark theme={theme} hollow maskId={maskId} />
      </svg>
    );
  }

  if (variant === 'wordmark') {
    return (
      <svg
        viewBox="0 0 200 44"
        className={cn('h-6 w-auto', className)}
        xmlns="http://www.w3.org/2000/svg"
        {...a11yProps}
      >
        {!isDecorative && <title id={labelledById}>{accessibleLabel}</title>}
        <Wordmark theme={theme} />
      </svg>
    );
  }

  // 'full': icon + wordmark side by side, proportional gap.
  return (
    <span className={cn('inline-flex items-center gap-2', className)} {...a11yProps}>
      {!isDecorative && <span id={labelledById} className="sr-only">{accessibleLabel}</span>}
      <svg viewBox={ICON_VIEWBOX} className="h-8 w-8 shrink-0" xmlns="http://www.w3.org/2000/svg" aria-hidden>
        <IconMark theme={theme} hollow maskId={`${maskId}-icon`} />
      </svg>
      <svg viewBox="0 0 200 44" className="h-6 w-auto" xmlns="http://www.w3.org/2000/svg" aria-hidden>
        <Wordmark theme={theme} />
      </svg>
    </span>
  );
}
