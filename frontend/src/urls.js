import { hashHistory } from 'react-router';
import { setupUrls } from 'phaceologyUtil';

export let history = hashHistory;

let urls = {
  home:'/',
  userList:'user',
  userDetail:(userId) => 'user/' + (userId || ':userId')
};

setupUrls(urls, history);

export default urls;

