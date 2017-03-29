import models from 'models';
import urls from 'lmsUrls';

let errorHandlers = [];

export function addErrorHandler(fn) {
  errorHandlers.push(fn);
}

export function handleError(error) {
  console.error('Error fetching data :', error);
  if (error.code === 119) { // Forbidden. We must not be logged in.
    models.User.logOut().then((user) => {
      urls.gotoHome();
    });
  }
  for (let handler of errorHandlers) {
    handler(error);
  }
}
