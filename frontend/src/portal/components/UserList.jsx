import React, { PropTypes } from 'react';

import { prop } from 'phaceologyUtil';

import UserRow from 'UserRow';

/** Renders a list of users in a nice table.
 prop users The User objects to render

 prop topDivisions A list of Division objects, each one at the top of the
 hierarchy, with a `children` field containing child divisions.
 */
export default function UserList({ users, topDivisions }) {
  function pushDivisions(rows, divisions, depth=0) {
    for (let division of divisions) {
      let divisionName = division.get('name') || "<Unnamed division>";
      for (let i = 0; i < depth; i++) {
        divisionName = ' * ' + divisionName;
      }
      rows.push(<tr key={ 'division-' + division.id }><th colSpan="3">{ divisionName }</th></tr>);
      let divUsers = users.filter((user) => (prop(user, 'division', {id:-1}).id === division.id));
      let userRows = divUsers.map((user) =>  <UserRow user={ user } key={ 'user-' + user.id } />);
      rows.push(...userRows);

      if (division.children) {
        pushDivisions(rows, division.children, depth + 1);
      }
    }
  }

  let nodivUsers = users.filter((user) => (!user.get('division')));
  let rows = nodivUsers.map((user) =>  <UserRow user={ user } key={ 'user-' + user.id } />);

  pushDivisions(rows, topDivisions);
  
  return (
    <div className="container">
      <h1>{ users.length } Users</h1>
      <table className="table table-striped table-hover">
        <thead>
          <UserRow isheader={ true }/>
        </thead>
        <tbody>
          { rows }
        </tbody>
      </table>
    </div>
  );
}

UserList.propTypes = {
  users:PropTypes.array.isRequired,
  topDivisions:PropTypes.array.isRequired
};

