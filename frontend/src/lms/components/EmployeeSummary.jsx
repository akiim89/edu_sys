import React, { PropTypes } from 'react';
import models from 'models';
import { prop } from 'phaceologyUtil';

export default function EmployeeSummary() {
  const user = models.User.current();

  console.log('EmployeeSummary: current user ', user);

  if (!user) {
    return null;
  }
  return (
    <div className="row user-badge">
      <div className="user-badge-divider">&nbsp;</div>
      <div className="col-xs-4 col-md-2 user-badge-profile-pic">
	<img  className="profile-pic img-circle" src={prop(user, 'profile_picture')} alt={prop(user, 'name')}/>
      </div>
      <div className="col-xs-8 col-md-3">
	<div className="row user-name">
	  {prop(user, 'name', 'Name')}
	</div>
	<div className="row user-division">
	  {prop(user, 'division.name', 'Employee')}
	</div>
	<div className="row user-percent-row">
	  <div className="col-xs-4 col-md-4 user-percent">
	    68<span className="user-percent-sign">%</span>
	  </div>
	  <div className="col-xs-8 col-md-2 user-percent-label">
	    Training Completed
	  </div>
	</div>
      </div>
    </div>
  );
}
