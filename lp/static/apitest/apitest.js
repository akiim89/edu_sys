var divisions = null;
function apitest() {
  console.log('logging in');
  // ES: Quick tests to see if the API is working ok.
  models.User.logIn('mgr.east@company2.com', 'Phace Demo').then(function(user) {
    console.log('logged in user ', user);
    console.log('got session token ', user.getSessionToken());
    console.log('getting all divisions');
    var query = new models.Query(models.Division);
    return query.find();
  }).then(function(results) {
    divisions = results;
    for (var i = 0; i < results.length; i++) {
      var object = results[i];
      console.log('Division ', i, ' objectId ', object.id, ' name ', object.get('name'));
    }
  }, function(error) {
    console.log("Error: " + error.code + " " + error.message);
  });
}


function updateDivision(division) {
  division.set('name', division.get('name') + '-bis');
  division.save();
}
