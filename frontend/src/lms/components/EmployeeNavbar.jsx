import React from 'react';
import Navbar from 'react-bootstrap/lib/Navbar';
import Button from 'react-bootstrap/lib/Button';
import { Link } from 'react-router';

import urls from 'lmsUrls';

import LogoutButton from 'LogoutButton.jsx';

export default function PortalNavbar(props) {
  const menuClicked = function(e) {
    if (props.onMenuClick) {
      props.onMenuClick(e);
    }
  };

  return (
    <Navbar fixedTop={true} role="navigation">
      <div className="container">
        <Navbar.Header>
          <Navbar.Toggle onClick={menuClicked} />
          <Link className="navbar-brand text-hide" to={urls.moduleList}>
            Phaceology
	  </Link>
        </Navbar.Header>
      </div>
    </Navbar>
  );
}

