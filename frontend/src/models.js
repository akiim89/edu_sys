import Parse from 'parse';
import PhaceologyRESTController from './PhaceologyRESTController';
//import './reactapp.jsx';

Parse.initialize("APPLICATION_ID", "JAVASCRIPT_KEY"); // Dummy values here, since we're not running a real Parse server.
Parse.serverURL = DJANGO_SETTINGS.URL_BASE + '/api/';
Parse.CoreManager.setRESTController(PhaceologyRESTController);

function facebookLogin(inviteCode, permissions, options) {
  if (inviteCode) {
    PhaceologyRESTController.setInviteCode(inviteCode);
  }
  return Parse.FacebookUtils.logIn(permissions, options);
}

var models = {
  Parse:Parse,
  Object:Parse.Object,
  User:Parse.User,
  Query:Parse.Query,
  facebookLogin:facebookLogin
};

for (var model of [
  'Division',
  'UserInvite',
  'Company',
  'PerformanceMetric',
  'PerformanceScore',
  'Lesson',
  'LessonModule',
  'LessonModuleCategory',
  'Role',
  'QuizQuestion',
  'QuizAnswer',
  'QuizAttempt',
  'QuizAnswerAttempt',
  'FacebookProfile'
]) {
  models[model] = Parse.Object.extend(model);
  Parse.Object.registerSubclass(model, models[model]);
}

export default models;


