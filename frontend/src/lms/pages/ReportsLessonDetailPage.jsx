import React from 'react';
import ReactDOM from 'react-dom';
import models from 'models';
import { urls } from 'lmsUrls';
import { handleError } from 'lmsUtil';
import { prop } from 'phaceologyUtil';

import StaticImage from 'StaticImage';
import ArrowCol from 'ArrowCol';
import LoaderAnimation from 'LoaderAnimation';
import ProfilePic from 'ProfilePic';
import { Link } from 'react-router';

////////////////////////////////////////////////////////////////////////////////
// Ugh, this page is a piece of shit. Trying to cram too much information onto
// one poorly designed page.


function DivisionHeaderRow({division}) {
  return (
    <div className="row division-header inverse two-part-row">
      <div className="col-xs-12">
	<div className="row row-header">
	  {prop(division, 'name')}
	</div>
	<div className="row row-detail">
	  {prop(division, 'description')}
	</div>
      </div>
    </div>
  );
}

function LessonHeaderRow({lesson}) {
  return (
    <div className="row lesson-header inverse">
      <div className="col-xs-12">
	{prop(lesson, 'name')}
      </div>
    </div>
  );
}

function EmployeeRow({user}) {
  return (
    <div className="row employee inverse inverse-linked-row">
      <Link to={urls.reportsEmployeeDetail(user.id)}>
	<div className="col-xs-3">
	  <ProfilePic user={user} small={true}/>
	</div>
	<div className="col-xs-8">
	  <div className="row name">
	    {prop(user, 'name')}
	  </div>
	  <div className="row role">
	    {prop(user, 'role')}
	  </div>
	</div>
	<ArrowCol inverse={true} alt="details"/>
      </Link>
    </div>
  );
}

export default class ReportsLessonDetailPage extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      employees:[],
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
    let userPromise = new models.Query(models.User)
	  .equalTo('division_id', this.props.params.divisionId)
	  .find();

    let divisionPromise = new models.Query(models.Division)
	  .get(this.props.params.divisionId);

    let lessonPromise = new models.Query(models.Lesson)
	  .get(this.props.params.lessonId);

    models.Parse.Promise.when([userPromise, divisionPromise, lessonPromise])
      .then((results) => {
	let [users, division, lesson] = results;

	if (!this.ignoreLastFetch) {
	  this.setState({users:users,
			 division:division,
			 lesson:lesson,
			 fetchInProgress:false});
	}
      }).fail(handleError);
  }

  render() {
    if (this.state.fetchInProgress ) {
      return (
	<div className="reports-lesson-detail-page">
	  <LoaderAnimation visible={true}/>
	</div>
      );
    }

    return (
      <div className="container reports-lesson-detail-page">
    	<div className="row page-header-row inverse">
    	  Reports
    	</div>
	<DivisionHeaderRow division={this.state.division}/>
	<LessonHeaderRow lesson={this.state.lesson}/>
	{ this.state.users.map((user) => <EmployeeRow user={user} key={user.id}/>) }
      </div>
    );
  }
}
