import React from 'react';
import { Link } from 'react-router';

import urls from 'urls';
import models from 'models';

/// A little component to create a link to a user's detail page with their
/// name.
export default function UserLink(props) {
  if (props.user) {
    return (
      <Link to={ urls.userDetail(props.user.id) }>{ models.prop(props.user, 'name', 'N/A') }</Link>
    );
  } else {
    return <span>N/A</span>;
  }
}

