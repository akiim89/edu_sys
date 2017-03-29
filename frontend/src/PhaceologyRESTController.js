/**
 * Copyright (c) 2015-present, Parse, LLC.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree. An additional grant
 * of patent rights can be found in the PATENTS file in the same directory.
 *
 * @flow
 */

import Parse from 'parse';

export type RequestOptions = {
  useMasterKey?: boolean;
  sessionToken?: string;
  installationId?: string;
};

export type FullOptions = {
  success?: any;
  error?: any;
  useMasterKey?: boolean;
  sessionToken?: string;
  installationId?: string;
};

function encodeData(data) {
  return Object.keys(data).map(function(key) {
    let value = data[key];
    if (typeof(value) === 'object') {
      value = JSON.stringify(value);
    }
    return [key, value].map(encodeURIComponent).join("=");
  }).join("&");
}

var XHR = null;
if (typeof XMLHttpRequest !== 'undefined') {
  XHR = XMLHttpRequest;
}
// if (process.env.PARSE_BUILD === 'node') {
//   XHR = require('xmlhttprequest').XMLHttpRequest;
// }

var useXDomainRequest = false;
if (typeof XDomainRequest !== 'undefined' &&
    !('withCredentials' in new XMLHttpRequest())) {
  useXDomainRequest = true;
}

function ajaxIE9(method: string, url: string, data: any) {
  var promise = new Parse.Promise();
  var xdr = new XDomainRequest();
  xdr.onload = function() {
    var response;
    try {
      response = JSON.parse(xdr.responseText);
    } catch (e) {
      promise.reject(e);
    }
    if (response) {
      if (Array.isArray(response)) {
        response = {'results':response}; // ES: Parse expects the results in an object with the key of results
      }
      promise.resolve(response);
    }
  };
  xdr.onerror = xdr.ontimeout = function() {
    // Let's fake a real error message.
    var fakeResponse = {
      responseText: JSON.stringify({
        code: Parse.Error.X_DOMAIN_REQUEST,
        error: 'IE\'s XDomainRequest does not supply error info.'
      })
    };
    promise.reject(fakeResponse);
  };
  xdr.onprogress = function() { };
  xdr.open(method, url);
  xdr.send(data);
  return promise;
}

var inviteCode;

const PhaceologyRESTController = {
  setInviteCode(code) {
    inviteCode = code;
  },

  ajax(method: string, url: string, data: any, headers?: any) {
    if (useXDomainRequest) {
      return ajaxIE9(method, url, data, headers);
    }

    let promise = new Parse.Promise();
    let attempts = 0;

    var dispatch = function() {
      if (XHR == null) {
        throw new Error(
          'Cannot make a request: No definition of XMLHttpRequest was found.'
        );
      }
      var handled = false;
      var xhr = new XHR();

      xhr.onreadystatechange = function() {
        if (xhr.readyState !== 4 || handled) {
          return;
        }
        handled = true;

        if (xhr.status >= 200 && xhr.status < 300) {
          var response;
          try {
            response = JSON.parse(xhr.responseText);
          } catch (e) {
            promise.reject(e.toString());
          }
          if (response) {
            if (Array.isArray(response)) {
              response = {'results':response}; // ES: Parse expects the results in an object with the key of results
            }
            promise.resolve(response, xhr.status, xhr);
          }
        } else if (xhr.status >= 500 || xhr.status === 0) { // retry on 5XX or node-xmlhttprequest error
          if (++attempts < Parse.CoreManager.get('REQUEST_ATTEMPT_LIMIT')) {
            // Exponentially-growing random delay
            var delay = Math.round(
              Math.random() * 125 * Math.pow(2, attempts)
            );
            setTimeout(dispatch, delay);
          } else if (xhr.status === 0) {
            promise.reject('Unable to connect to the Parse API');
          } else {
            // After the retry limit is reached, fail
            promise.reject(xhr);
          }
        } else {
          promise.reject(xhr);
        }
      };

      headers = headers || {};
      if (typeof(headers['Content-Type']) !== 'string') {
        headers['Content-Type'] = 'application/json'; // ES: Changed from text/plain
      }

      if (Parse.CoreManager.get('IS_NODE')) {
        headers['User-Agent'] = 'Parse/' + Parse.CoreManager.get('VERSION') +
          ' (NodeJS ' + process.versions.node + ')';
      }
      headers['Accept'] = 'application/json'; // ES: Added for Django REST Framework

      xhr.open(method, url, true);
      for (var h in headers) {
        xhr.setRequestHeader(h, headers[h]);
      }
      xhr.send(data);
    };
    dispatch();

    return promise;
  },

  request(method: string, path: string, data: mixed, options?: RequestOptions) {
    options = options || {};
    var headers = {};
    var url = Parse.CoreManager.get('SERVER_URL');
    if (url[url.length - 1] !== '/') {
      url += '/';
    }
    url += path;
    // ES: Django paths end in a slash.
    if (url[url.length - 1] !== '/') {
      url += '/';
    }

    var payload = {};
    if (data && typeof data === 'object') {
      // ES: This is hacky unfortunately, but I can't see any other way to hook
      // into the Facebook linking process.
      if (data.authData && typeof data.authData.facebook === 'object' && inviteCode) {
        data.authData.facebook.invite_code = inviteCode;
      }

      for (var k in data) {
        payload[k] = data[k];
      }
    }


    // ES: Parse turns GETs into POSTs with a _method param. I think this is for
    // cross-origin support maybe?
/*    if (method !== 'POST') {
      payload._method = method;
      method = 'POST';
    }
*/
    // ES: This stuff doesn't apply to Django REST at the moment:
    // payload._ApplicationId = Parse.CoreManager.get('APPLICATION_ID');
    // let jsKey = Parse.CoreManager.get('JAVASCRIPT_KEY');
    // if (jsKey) {
    //   payload._JavaScriptKey = jsKey;
    // }
    payload._ClientVersion = Parse.CoreManager.get('VERSION');

    // ES: This stuff doesn't apply to Django REST at the moment:
    // var useMasterKey = options.useMasterKey;
    // if (typeof useMasterKey === 'undefined') {
    //   useMasterKey = Parse.CoreManager.get('USE_MASTER_KEY');
    // }
    // if (useMasterKey) {
    //   if (Parse.CoreManager.get('MASTER_KEY')) {
    //     delete payload._JavaScriptKey;
    //     payload._MasterKey = Parse.CoreManager.get('MASTER_KEY');
    //   } else {
    //     throw new Error('Cannot use the Master Key, it has not been provided.');
    //   }
    // }

    // if (Parse.CoreManager.get('FORCE_REVOCABLE_SESSION')) {
    //   payload._RevocableSession = '1';
    // }

    var installationId = options.installationId;
    var installationIdPromise;
    if (installationId && typeof installationId === 'string') {
      installationIdPromise = Parse.Promise.as(installationId);
    } else {
      var installationController = Parse.CoreManager.getInstallationController();
      installationIdPromise = installationController.currentInstallationId();
    }

    return installationIdPromise.then((iid) => {
      payload._InstallationId = iid;
      var userController = Parse.CoreManager.getUserController();
      if (options && typeof options.sessionToken === 'string') {
        return Parse.Promise.as(options.sessionToken);
      } else if (userController) {
        return userController.currentUserAsync().then((user) => {
          if (user) {
            return Parse.Promise.as(user.getSessionToken());
          }
          return Parse.Promise.as(null);
        });
      }
      return Parse.Promise.as(null);
    }).then((token) => {
      if (token) {
        payload._SessionToken = token;
        headers['Authorization'] = 'Token ' + token;
      }

      var payloadString = JSON.stringify(payload);
      if (method === 'GET' || method === 'HEAD') {
        url = url + '?' + encodeData(payload);
        payloadString = null;
      }

      return PhaceologyRESTController.ajax(method, url, payloadString, headers);
    }).then(null, function(response: { responseText: string }) {
      // Transform the error into an instance of Parse.Error by trying to parse
      // the error string as JSON
      var error;
      if (response && response.responseText) {
        try {
          var errorJSON = JSON.parse(response.responseText);
          if (response.status === 401) {
            //OperationForbidden
            error = new Parse.Error(119, errorJSON.detail);
          } else {
            error = new Parse.Error(errorJSON.code, errorJSON.error);
          }
        } catch (e) {
          // If we fail to parse the error text, that's okay.
          error = new Parse.Error(
            Parse.Error.INVALID_JSON,
            'Received an error with invalid JSON from Parse: ' +
              response.responseText
          );
        }
      } else {
        error = new Parse.Error(
          Parse.Error.CONNECTION_FAILED,
          'XMLHttpRequest failed: ' + JSON.stringify(response)
        );
      }

      return Parse.Promise.error(error);
    });
  },

  _setXHR(xhr: any) {
    XHR = xhr;
  }
}

module.exports = PhaceologyRESTController;
