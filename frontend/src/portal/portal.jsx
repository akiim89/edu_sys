import React from 'react';
import ReactDOM from 'react-dom';

import BootstrapCss from 'bootstrap/dist/css/bootstrap.css';

// import Button from 'react-bootstrap/lib/Button';
// import Nav from 'react-bootstrap/lib/Nav';
// import FormGroup from 'react-bootstrap/lib/FormGroup';
// import FormControl from 'react-bootstrap/lib/FormControl';

import { Router, Route, IndexRoute } from 'react-router';

import models from 'models';
import PortalNavbar from 'PortalNavbar';
import UserListPage from 'UserListPage';
import UserDetailPage from 'UserDetailPage';
import urls, { history } from 'urls';

// const element = navbar;
// ReactDOM.render(
//   element,
//   document.getElementById('here')
// );

class LoginView extends React.Component {
  constructor(props) {
    super(props);
    this.handleChange = this.handleChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
    this.state = {
      email:'',
      password:''
    };
  }
  
  componentDidMount () {
    this.checkLogin();
  }

  checkLogin() {
    console.log('checkLogin');
    let that = this;
    models.User.currentAsync().then(function(user) {
      console.log('checkLogin: current user ', user);
      if (user.authenticated) {
        console.log('checkLogin: is authenticated');
        urls.gotoUserList();
      }
    });
  }

  handleChange(event) {
    let stateParams = {};
    stateParams[event.target.name] = event.target.value;
    console.log('LoginView:handleChange: ', stateParams);
    this.setState(stateParams);
  }

  handleSubmit(event) {
    event.preventDefault();

    console.log('LoginView:handleSubmit: email ', this.state.email, ' password ', this.state.password);
    if (this.state.email.length && this.state.password.length) {
      console.log('LoginView:handleSubmit: logging in');
      let that = this;
      models.User.logIn(this.state.email, this.state.password).then(function(user) {
        console.log('LoginView:handleSubmit: logged in success. user ', user, ' this ', this);
        that.checkLogin();
      });
    }
  }
  
  render() {
    return (
      <div className="jumbotron">
        <div className="container">
          <h1>Welcome</h1>
          <form className="form col-md-4" role="form" onSubmit={this.handleSubmit}>
            <div className="form-group">
              <input type="text" placeholder="Email" name="email" className="form-control" value={this.state.email} onChange={this.handleChange}/>
            </div>
            <div className="form-group">
              <input type="password" placeholder="Password" name="password" className="form-control" value={this.state.password} onChange={this.handleChange}/>
            </div>
            <button type="submit" className="btn btn-primary btn-lg">Sign in &raquo;</button>
          </form>
        </div>
      </div>
    );
  }
}

const App = React.createClass({
  render() {
    return (
      <div>
        <PortalNavbar />
        {this.props.children}
      </div>
    );
  }
});

ReactDOM.render((
  <Router history={history}>
    <Route path="/" component={App}>
      <IndexRoute component={LoginView} />
      <Route path={urls.userList} component={UserListPage} />
      <Route path={urls.userDetail()} component={UserDetailPage} />
    </Route>
  </Router>
), document.getElementById('react-content'));

module.exports = {models:models};
