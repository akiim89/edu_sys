/*global FB */

import models from '../models';

var inited = false;
var initCallbacks = [];

window.fbAsyncInit = function() {
  models.Parse.FacebookUtils.init({ // this line replaces FB.init({
    appId      : DJANGO_SETTINGS.FACEBOOK_APP_ID, // Facebook App ID
    status     : false,  // check Facebook Login status
    cookie     : true,  // enable cookies to allow Parse to access the session
    xfbml      : true,  // initialize Facebook social plugins on the page
    version    : 'v2.3' // point to the latest Facebook Graph API version
  });

  inited = true;
  // Run code after the Facebook SDK is loaded.
  for (let fn of initCallbacks) {
    fn();
  }
  initCallbacks = null;
};

(function(d, s, id){
  var js, fjs = d.getElementsByTagName(s)[0];
  if (d.getElementById(id)) {return;}
  js = d.createElement(s); js.id = id;
  js.src = "//connect.facebook.net/en_US/sdk.js";
  fjs.parentNode.insertBefore(js, fjs);
}(document, 'script', 'facebook-jssdk'));

const PHFacebookLogin = {
  getLoginStatus() {
    return new Promise((resolve, reject) => {
      let checker = () => {
	FB.getLoginStatus((response) => {
	  resolve(response);
	});
      };
      if (inited) {
	checker();
      } else {
	initCallbacks.push(checker);
      }
    });
  }
};

export default PHFacebookLogin;
