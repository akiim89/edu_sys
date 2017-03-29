import React, { PropTypes } from 'react';

let imgSrc = DJANGO_SETTINGS.STATIC_URL + 'img/';

export default function StaticImage({src, alt, className}) {
  return <img src={ imgSrc + src } alt={alt} className={className}/>;
}

StaticImage.propTypes = {
  src:PropTypes.string.isRequired,
  alt:PropTypes.string.isRequired
};
