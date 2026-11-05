import React, { useState } from 'react';

// Stable hue per set so fallback tiles are distinguishable.
function hue(text = '') {
  let h = 0;
  for (let i = 0; i < text.length; i += 1) h = (h * 31 + text.charCodeAt(i)) % 360;
  return h;
}

const TYPE_ABBR = {
  'Booster Box': 'BB',
  'Elite Trainer Box': 'ETB',
  'Booster Bundle': 'BND',
  'Premium Collection': 'UPC',
};

/** Product image, or a colored tile with the product type if the image is missing or fails to load. */
export default function ProductThumb({ src, name, setName, productType, size = 44 }) {
  const [failed, setFailed] = useState(false);
  const style = { width: size, height: size };

  if (src && !failed) {
    return <img className="thumb" src={src} alt="" style={style} loading="lazy" onError={() => setFailed(true)} />;
  }
  const h = hue(setName || name);
  return (
    <span
      className="thumb thumb--tile"
      style={{ ...style, background: `linear-gradient(135deg, hsl(${h} 55% 32%), hsl(${(h + 40) % 360} 60% 22%))` }}
      aria-hidden="true"
    >
      {TYPE_ABBR[productType] || (productType || '?').slice(0, 3).toUpperCase()}
    </span>
  );
}
