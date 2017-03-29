import React from 'react';
import Navbar from 'react-bootstrap/lib/Navbar';
import Button from 'react-bootstrap/lib/Button';

import urls from 'urls';

import LogoutButton from 'LogoutButton';

export default function PortalNavbar(props) {
  return (
    <Navbar inverse={true} fixedTop={true} role="navigation">
      <div className="container">
        <Navbar.Header>
          <Navbar.Toggle />
        </Navbar.Header>
        <Navbar.Brand>
          <a href={urls.home}>Phaceology</a>
        </Navbar.Brand>
        <Navbar.Collapse>
          <LogoutButton urls={urls} />
        </Navbar.Collapse>      
      </div>
    </Navbar>
  );
}

