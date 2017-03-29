import React from 'react';

import models from 'models';
import urls from 'urls';
import { prop } from 'phaceologyUtil';

import UserList from 'UserList';

// Keep a local cache of the users, so we don't have to do a new fetch every
// time we navigate to this route.

// ES: FIXME: This is insecure!! This page needs redoing anyway. At that time,
// make sure to clear any caching when a user logs out, or just don't bother
// with it.
var cache = {
  users:[],
  topDivisions:[],
  currentUser:null
};

function setFind(haystack, fn) {
  for (let el of haystack) {
    if (fn(el)) {
      return el;
    }
  }
  return undefined;
}



export default class UserListPage extends React.Component {
  // The list of users view. Keep it very simple for now: no filtering, no pagination.
  constructor(props) {
    super(props);
    let currentUser = models.User.current();
    // Check for login/out. Clear the cache if the user changed.
    if (!cache.currentUser || cache.currentUser.id !== currentUser.id) {
      cache.users = [];
      cache.topDivisions = [];
      cache.currentUser = currentUser;
    }
    this.state = {
      users:cache.users,
      topDivisions:cache.topDivisions,
      currentUser:cache.currentUser
    };
  }
  
  componentDidMount () {
    // Fetch data initially
    this.ignoreLastFetch = false;
    this.fetchUsers();
  }

  componentDidUpdate (prevProps) {
    // Respond to parameter change.
    // NOTE: No parameters for now. Other classes might need this, or we might need it later.
  }

  componentWillUnmount () {
    // Ignore an inflight request.
    this.ignoreLastFetch = true;
  }

  fetchUsers () {
    new models.Query('User').include('division').find().then((result) => {
      if (!this.ignoreLastFetch) {
        const topDivisions = this.calculateDivisions(result);
        cache.users = result;
        cache.topDivisions = topDivisions;
        this.setState({ users: result, topDivisions:topDivisions });
      }
    }).fail((error) => {
      // TODO: Fill in.
      console.error('Error fetching users :', error);
      if (error.code === 119) { // Forbidden. We must not be logged in.
        models.User.logOut().then((user) => {
          urls.gotoHome();
        });
      }
    });
  }

  calculateDivisions(users) {
    // This function organizes all the users' divisions into a hierarchy. It's a
    // bit messy - TODO: clean it up or replace it.

    // Find all the unique divisions (that is, with unique ids. The objects may be duplicates).
    let divisions = [];
    for (let u of users) {
      let userDiv = u.get('division');
      if (userDiv && !divisions.find((d) => d.id === userDiv.id)) {
        divisions.push(userDiv);
      }
    }
    let topDivisions = new Set();

    for (let division of divisions) {
      if (division) {

        let parent =  division.get('parent');
        if (parent) {
          division.parent = setFind(divisions, (d) => d.id === parent.id);
        }

        if (division.parent) {
          let siblings = division.parent.children || new Set();
          siblings.add(division);
          division.parent.children = siblings;
        } else {
          topDivisions.add(division);
        }
      }
    }
    return topDivisions;
  }

  pushDivisions(rows, divisions, depth=0) {
    for (let division of divisions) {
      let divisionName = division.get('name') || "<Unnamed division>";
      for (let i = 0; i < depth; i++) {
        divisionName = ' * ' + divisionName;
      }
      rows.push(<tr key={ 'division-' + division.id }><th colSpan="3">{ divisionName }</th></tr>);
      let divUsers = this.state.users.filter((user) => (prop(user, 'division', {id:-1}).id === division.id));
      let userRows = divUsers.map((user) =>  <UserRow user={ user } key={ 'user-' + user.id } />);
      rows.push(...userRows);

      if (division.children) {
        this.pushDivisions(rows, division.children, depth + 1);
      }
    }
  }

  render () {
    return <UserList users={ this.state.users } topDivisions={this.state.topDivisions} />;
  }
}
