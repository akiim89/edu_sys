import React, { PropTypes} from 'react';

import urls from 'urls';
import { prop } from 'phaceologyUtil';

export default function UserRow({ user, isHeader }) {

  function handleClick(event) {
    urls.gotoUserDetail(user.id);
  }

  if (isHeader) {
    return (
      <tr>
        <th>Name</th>
        <th>Email</th>
        <th>Division</th>
      </tr>
    );
  }

  const name = prop(user, 'name');
  const email = prop(user, 'email');
  const divisionName = prop(user, 'division.name');

  return (
    <tr onClick={handleClick}>
      <td>{ name }</td>
      <td>{ email }</td>
      <td>{ divisionName }</td>
    </tr>
  );
}

UserRow.propTypes = {
  user:PropTypes.object,
  isHeader:PropTypes.boolean
};

