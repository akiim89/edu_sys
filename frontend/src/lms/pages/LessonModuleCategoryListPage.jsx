import React from 'react';

import models from 'models';
import urls from 'lmsUrls';
import { prop } from 'phaceologyUtil';
import { handleError } from 'lmsUtil';

import LessonModuleCategoryRow from 'LessonModuleCategoryRow';
import EmployeeSummary from 'EmployeeSummary';
import LoaderAnimation from 'LoaderAnimation';

export default class LessonModuleCategoryListPage extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      categories:[],
      quizAttempts:[],
      fetchInProgress:true
    };
  }
  
  componentDidMount () {
    // Fetch data initially
    this.fetchData();
  }

  componentWillUnmount () {
    // Ignore an inflight request.
    this.ignoreLastFetch = true;
  }

  fetchData() {
    let categoryPromise = new models.Query('LessonModuleCategory')
     	  .include('modules')
     	  .include('modules.lesson')
     	  .find();
    let quizAttemptPromise = new models.Query('QuizAttempt')
	  .equalTo('user', models.User.current())
	  .find();

    models.Parse.Promise.when([categoryPromise, quizAttemptPromise]).then((results) => {
      if (!this.ignoreLastFetch) {
        // TODO: Go through the quiz attempts and mark lessons as passed/failed.

	const categories = results[0];
	const quizAttempts = results[1];

	// Figure out the percent complete for each module.
	for (let cat of categories) {
	  for (let module of prop(cat, 'modules')) {
	    let lessons = prop(module, 'lessons');
	    module.nLessons = lessons.length;
	    module.nPassed = 0;
	    for (let lesson of lessons) {
	      // Look for a passing quiz attempt.
	      if (quizAttempts.find((qa) => (prop(qa, 'lesson').id === lesson.id &&
					     prop(qa, 'passed')))) {
		lesson.passed = true;
		module.nPassed++;
	      }
	    }
	    module.percentComplete = 100.0 * module.nPassed / module.nLessons;
	  }
	}
	      
        this.setState({categories:categories,
                       quizAttempts:quizAttempts,
                       fetchInProgress:false});
      }
    }).fail(handleError);
  }

  render () {
    return (
      <div className="container">
	<LoaderAnimation visible={this.state.fetchInProgress}/>
	<EmployeeSummary/>
	{ this.state.categories.map((category) => (
	  <LessonModuleCategoryRow category={category} key={category.id}/>
	)) }
      </div>
    );
  }
}
