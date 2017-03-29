// URLs for the Learning Management System (lms).

import { hashHistory } from 'react-router';
import { setupUrls } from 'phaceologyUtil';

export let history = hashHistory;

console.log('history.push is ', history.push);

function url(path, paramName) {
  if (paramName) {
    return (val) => path + '/' + (val || ':' + paramName);
  } else {
    return () => path;
  }
}

// ES: FIXME: I don't like the way some of these URLs are strings and some are
// functions. What if I make them all functions? (See above `url` function which
// could help with that.)

export let urls = {
  home:'/',
  settings:'settings',
  moduleList:'module',
  lessonList:(moduleId) => 'module/' + (moduleId || ':moduleId'),
  lessonDetail:(lessonId) => 'lesson/' + (lessonId || ':lessonId'),
  quizDetail:(quizId) => 'quiz/' + (quizId || ':lessonId'),

  reportsDivisionList:'reports',
  reportsDivisionDetail:(divisionId) => 'reports/' + (divisionId || ':divisionId'),
  reportsEmployeeDetail:(userId) => 'reports/employee/' + (userId || ':userId'),
  reportsLessonDetail:(divisionId, lessonId) => 'reports/' + (divisionId || ':divisionId') + '/lesson/' +  (lessonId || ':lessonId'),

  practicumDivisionList:'practicum',
  practicumLessonDetail:(lessonId, userId) => 'practicum/lesson/' + (lessonId || ':lessonId') + '/employee/' + (userId || ':userId')
};

setupUrls(urls, history);

export default urls;

