import React from 'react';
import StaticImage from 'StaticImage';
import { Link } from 'react-router';

import models from 'models';
import { prop } from 'phaceologyUtil';
import urls, { history } from 'lmsUrls.js';

function MenuItem({label, img, href, onClick}) {
  return (
      <div className="employee-menu-item">
	<Link to={href} onClick={onClick}>
	  <StaticImage src={img} className="employee-menu-icon" alt="Profile pic" />
	  {label}
	</Link>
      </div>
  );
}

export default function EmployeeMenu({visible, canViewReports}) {
  if (!visible) {
    return null;
  }
  const user = models.User.current();
  if (!user) {
    return <div>Not logged in</div>;
  }
  const logout = function(ev) {
    ev.preventDefault();
    models.User.logOut().then((user) => {
      urls.gotoHome();
    });
  };
  return (
    <div className="employee-menu">
      <div className="employee-menu-header">
	<div className="row menu-profile-pic-row">
	  <img  className="profile-pic img-circle" src={prop(user, 'profile_picture')} alt={prop(user, 'name')}/>
	</div>
	<div className="row employee-menu-user-name">
	  {prop(user, 'name', 'Name')}
	</div>
	<div className="row employee-menu-user-division">
	  {prop(user, 'division.name', 'Employee')}
	</div>
      </div>
      <MenuItem label="Training" img="training.svg" href={urls.moduleList}/>
      <MenuItem label="Notifications" img="notifications.svg"/>
      <MenuItem label="Settings" img="settings.svg" href={urls.settings}/>
      <MenuItem label="Phace Score" img="phace.svg"/>
      <MenuItem label="Pay" img="pay.svg"/>
      {canViewReports && <MenuItem label="Reports" img="settings.svg" href={urls.reportsDivisionList}/> }
      {canViewReports && <MenuItem label="Practicum" img="settings.svg" href={urls.practicumDivisionList}/> }
      <MenuItem label="Logout" img="settings.svg" onClick={logout}/>
    </div>
  );    
}
