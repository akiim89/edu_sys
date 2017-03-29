import React from 'react';
import ReactDOM from 'react-dom';
import StaticImage from 'StaticImage';

export default function ArrowCol({inverse, expanded, alt}) {
  let classes = 'col-xs-1 arrow-col';
  if (expanded) {
    classes += ' arrow-col-expanded';
  }
  let imgSrc = inverse ? 'arrow.svg' : 'whitearrow.svg';
  return (
    <div className={classes}>
      <StaticImage alt={alt} src={imgSrc}/>
    </div>
  );

}
