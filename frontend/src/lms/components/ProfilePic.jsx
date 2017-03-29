import React, { PropTypes } from 'react';
import models from 'models';
import { prop } from 'phaceologyUtil';

let defaultImage = DJANGO_SETTINGS.STATIC_URL + 'img/anonymous-profile-pic.jpg';
const defaultClassName = 'profile-pic img-circle';

export default function ProfilePic({className, user, small}) {
  user = user || models.User.current();
  let imgSrc = prop(user, 'profile_picture', defaultImage);
  
  let theClassName = defaultClassName;
  if (className) {
    theClassName = theClassName + ' ' + className;
  }
  if (small) {
    theClassName += ' profile-pic-small';
  }
  return (
    <img className={theClassName} src={imgSrc} alt="Profile Picture"/>
  );
}
