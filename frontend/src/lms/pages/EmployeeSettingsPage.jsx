import React, { PropTypes } from 'react';

import ProfilePic from 'ProfilePic';

import { prop } from 'phaceologyUtil';
import models from '../../models.js';
import urls from '../lmsUrls.js';

function SettingsItem({label, value}) {
  return (
    <div className="employee-settings-item">
      <div className="row employee-settings-item-label">
	<div className="col-xs-12 col-md-offset-3 col-md-6">
	  {label}
	</div>	  
      </div>
      <div className="row employee-settings-item-value">
	<div className="col-xs-12 col-md-offset-3 col-md-6">
	  {value}
	</div>
      </div>
    </div>
  );
}

export default class EmployeeSettingsPage extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
    };
  }

  componentDidMount () {
  }

  componentDidUpdate (prevProps) {
  }

  componentWillUnmount () {
  }

  render () {
    const user = models.User.current();
    return (
      <div className="container employee-settings-page">
	
	<div className="row employee-settings-profile-pic-row">
	  <div className="col-xs-4 col-md-offset-3 col-md-2">
	    <ProfilePic />
	  </div>
	  <div className="col-xs-8 col-md-4">
	    <div className="row employee-settings-profile-pic-label">
	      Profile Picture
	    </div>
	    <div className="row employee-settings-profile-pic-button">
	      <input className="btn btn-default" type="button" value="Upload New Image" />
	    </div>
	  </div>
	</div>

	<SettingsItem label="Name" value={prop(user, 'name', '[N/A]')}/>
	<SettingsItem label="Email" value={prop(user, 'email', '[N/A]')}/>
	<SettingsItem label="Phone" value={prop(user, 'phone', '[N/A]')}/>
	
      </div>
    );
  }
}
