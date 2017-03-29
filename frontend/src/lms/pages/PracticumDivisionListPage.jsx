import React from 'react';
import ReactDOM from 'react-dom';
import models from 'models';
import { urls } from 'lmsUrls';
import { handleError } from 'lmsUtil';
import { prop } from 'phaceologyUtil';

import StaticImage from 'StaticImage';
import LoaderAnimation from 'LoaderAnimation';
import ProfilePic from 'ProfilePic';
import { Link } from 'react-router';

function LessonRow({user, lesson}) {
  return (
    <div className="row lesson">
      <div className="col-xs-10 lesson-name">
	{ prop(lesson, 'name') }
      </div>
      <div className="col-xs-2 lesson-button-col">
	<Link className="start-button" type="button" to={urls.practicumLessonDetail(lesson.id, user.id)}>Start</Link>
      </div>
    </div>
  );
}

class EmployeeSection extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      expanded:false
    };
    this.toggleExpand = this.toggleExpand.bind(this);
  }

  toggleExpand() {
    this.setState((prevProps) => ({expanded:!prevProps.expanded}));
  }

  render() {
    const user = this.props.user;
    if (this.state.expanded) {
      return (
	<div className="employee-section employee-expanded">
	  <div className="row employee" onClick={this.toggleExpand}>
	    <div className="col-xs-3">
	      <ProfilePic user={user}/>
	    </div>
	    <div className="col-xs-8">
	      <div className="row name">
		{prop(user, 'name')}
	      </div>
	      <div className="row role">
		{prop(user, 'role')}
	      </div>
	    </div>
	    <div className="col-xs-1 arrow-col">
	      <StaticImage alt="expand" src="whitearrow.svg"/>
	    </div>
	  </div>
	  {this.props.lessons.map((lesson) => (
	    <LessonRow user={user} lesson={lesson} key={lesson.id}/>
	    )
	  )}
	</div>
      );
    } else {
      return (
	<div className="employee-section">
	  <div className="row employee inverse" onClick={this.toggleExpand}>
	    <div className="col-xs-3">
	      <ProfilePic user={user}/>
	    </div>
	    <div className="col-xs-8">
	      <div className="row name">
		{prop(user, 'name')}
	      </div>
	      <div className="row role">
		{prop(user, 'role')}
	      </div>
	    </div>
	    <div className="col-xs-1 arrow-col">
	      <StaticImage alt="expand" src="arrow.svg"/>
	    </div>
	  </div>
	</div>
      );
    }
  }
}

function DivisionRow({division}) {
  return (
    <div className="row division-row">
      <div className="col-xs-12">
	{prop(division, 'name')}
      </div>
    </div>
  );
}

function DivisionSection({division, lessons}) {
  const users = prop(division, 'employees');
  return (
    <div className="division-section">
      <DivisionRow division={division}/>
      { users.map((user) => <EmployeeSection user={user} lessons={lessons} key={user.id} /> ) }
    </div>
  );
}

export default class PracticumDivisionListPage extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      divisions:[],
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
    let divisionPromise = new models.Query(models.Division)
	  .include('employees')
	  .find();

    let lessonsPromise = new models.Query(models.Lesson).find();
    
    models.Parse.Promise.when([divisionPromise, lessonsPromise])
      .then((results) => {
	if (!this.ignoreLastFetch) {
	  const [divisions, lessons] = results;
	  console.log('got divisions ', divisions);
	  console.log('got lessons ', lessons);
	  this.setState({divisions:divisions, lessons:lessons, fetchInProgress:false});
	}
      }).fail(handleError);
  }

  render() {
    const waitingView = (
	<div className="reports-division-list-page">
	  <LoaderAnimation visible={true}/>
	</div>
      );

    if (this.state.fetchInProgress) {
      return (
	<div className="practicum-division-list-page">
	  <LoaderAnimation visible={true}/>
	</div>
      );
    }

    return (
      <div className="container practicum-division-list-page">
	<div className="row page-header-row inverse">
	  Practicum
	</div>
	{ this.state.divisions.map(division => <DivisionSection division={division} lessons={this.state.lessons} key={division.id}/>) }
      </div>
    );
  }
}
