import React from 'react';
import StaticImage from 'StaticImage';

export default function LoaderAnimation({visible}) {
  if (!visible) {
    return null;
  }
  return (
     <div className="loader"/>
  );
}
