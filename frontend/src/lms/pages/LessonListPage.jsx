import React from 'react';
import { Link } from 'react-router';

import StaticImage from 'StaticImage';
import LoaderAnimation from 'LoaderAnimation';

import models from 'models';
import urls from 'lmsUrls';
import { prop } from 'phaceologyUtil';
import { handleError } from 'lmsUtil';

function Check({checked}) {
  if (checked) {
    return <StaticImage alt="checked" src="check.svg" className="check"/>;
  } else {
    return <div className="check"/>;
  }    
}

function LessonRow({lesson}) {
  let checked = !!lesson.passed;
  return (
    <div className="row lesson linked-row">
      <Link to={urls.lessonDetail(lesson.id)}>
	<div className="col-xs-1 lesson-check">
	  <Check checked={checked}/>
	</div>
	<div className="col-xs-10">{prop(lesson, 'name', "[N/A]")}</div>
	<div className="col-xs-1 lesson-arrow-col">
	  <StaticImage className="lesson-arrow" src="whitearrow.svg" alt="More"/>
	</div>
      </Link>
    </div>
  );
}

function LessonListHeader({module}) {
  return (
    <div>
      <div className="row lesson-list-header">
	<div className="col-xs-1 back-arrow">
	  <Link to={urls.moduleList}>
	    <StaticImage alt="back" className="lesson-list-header-back" src="whitearrow.svg"/>
	  </Link>
	</div>
	<div className="col-xs-8 module-name">
	  {prop(module, 'name')}
	</div>
	<div className="col-xs-3 percent-complete">
	  <div className="number">{module ? module.percentComplete : "N/A"}%</div>
	  <div className="text">Complete</div>
	</div>
      </div>
      <div className="row lesson-list-lower-header">
	<div className="col-xs-offset-8 col-xs-4">% Complete</div>
      </div>
    </div>
  );
}

export default class LessonListPage extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      lessons:[],
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
    let modulePromise = new models.Query('LessonModule')
	  .include('lessons')
	  .get(this.props.params.moduleId);

    let quizAttemptPromise = new models.Query('QuizAttempt')
	  .equalTo('user', models.User.current())
	  .find();

    models.Parse.Promise.when([modulePromise, quizAttemptPromise]).then((results) => {
      console.log('LessonListPage.got data ', results);
      if (!this.ignoreLastFetch) {
	const [module, quizAttempts] = results;
	
	const lessons = prop(module, 'lessons');
	
	// Figure out the percent complete for the module and whether each lesson passed.
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

        this.setState({module:module,
		       lessons:lessons,
                       quizAttempts:results[1],
                       fetchInProgress:false});
      }
    }).fail(handleError);
  }

  render () {
    const lessons = this.state.lessons;
    console.log('lessons ', lessons);
    let rows = lessons.map((lesson) => <LessonRow lesson={lesson} key={lesson.id}/>);
    return (
      <div className="container" style={{position:'relative'}}>
	<LoaderAnimation visible={this.state.fetchInProgress}/>
	<LessonListHeader module={this.state.module}/>
	{ rows }
      </div>
    );
  }
}
