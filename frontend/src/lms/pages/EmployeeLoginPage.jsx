import React from 'react';
import ReactDOM from 'react-dom';

import PHFacebookLogin from 'facebookLogin';
import models from 'models';
import { history, urls } from 'lmsUrls';


export default class EmployeeLoginPage extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
    };
    this.handleLoginClick = this.handleLoginClick.bind(this);
  }

  componentDidMount() {
    PHFacebookLogin.getLoginStatus().then(this.checkLogin.bind(this));
  }

  componentWillUnmount() {
  }    

  checkLogin(response) {
    console.log('checkLogin: ', response);
    const user = models.User.current();
    if (user && user.authenticated) {
      console.log('checkLogin: is authenticated ', user);
      urls.gotoModuleList();
    }
  }

  handleLoginClick(ev) {
    ev.preventDefault();
    const inviteCode = ev.target.parentNode.querySelector('#invite-code').value;
    console.log('handleLoginClick: inviteCode ', inviteCode);
    models.facebookLogin(inviteCode, 'email,public_profile,user_photos', {
      success:function(response){
        // Handle the response object, like in statusChangeCallback() in our demo
        // code.
        console.log('logged in ', response);
	urls.gotoModuleList();
      },
      error:function(er) {
        console.error('FB login error ', er);
      }
    });
  }
    
  render() {
    return (
      <div className="container">
        <form>
          <div className="form-group">
            <h1>Login please</h1>
            <label htmlFor="invite-code">Invite Code</label>
            <input type="text" className="form-control" id="invite-code" placeholder="Invite Code" />
            <button className="btn btn-default" type="submit" onClick={this.handleLoginClick}>Login</button>
          </div>
        </form>
      </div>
    );
  }
}
