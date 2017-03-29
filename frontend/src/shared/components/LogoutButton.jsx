import React from 'react';
import Nav from 'react-bootstrap/lib/Nav';
import NavItem from 'react-bootstrap/lib/NavItem';

import models from 'models';

export default class LogoutButton extends React.Component {
  constructor(props) {
    super(props);
    this.handleClick = this.handleClick.bind(this);
  }

  handleClick(event) {
    models.User.logOut().then((user) => {
      this.props.urls.gotoHome();
    });
  }

  render() {
    return (
     <Nav pullRight>
       <NavItem href="#" onClick={this.handleClick}>Log Out</NavItem>
      </Nav>
    );
  }
}

