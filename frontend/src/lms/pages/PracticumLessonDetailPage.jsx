import React from 'react';
import ReactDOM from 'react-dom';
import models from 'models';
import { urls } from 'lmsUrls';
import { handleError } from 'lmsUtil';
import { prop } from 'phaceologyUtil';

import LoaderAnimation from 'LoaderAnimation';

export default class PracticumLessonDetailPage extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      submittingResult:false
    };
    this.passWasClicked = this.passWasClicked.bind(this);
    this.failWasClicked = this.failWasClicked.bind(this);
  }
  
  componentDidMount () {
    // Fetch data initially
    this.fetchData();
  }

  componentWillUnmount () {
    // Ignore an inflight request.
    this.ignoreLastFetch = true;
  }

  passWasClicked() {
    this.setResult(100);
  }

  failWasClicked() {
    this.setResult(0);
  }

  setResult(score) {
    if (this.state.submittingResult) {
      return;
    }
    this.setState({submittingResult:true});
    console.log('employeeId is ', this.props.params.userId);
    models.Parse.Cloud.run('manualResult', {userId:this.props.params.userId,
					    lessonId:this.props.params.lessonId,
					    score:score})
      .then((result) => {
	urls.gotoPracticumDivisionList();
      }).fail(handleError);
  }

  fetchData() {
  }

  render() {
    return (
      <div className="container practicum-lesson-detail-page inverse">
	<div className="row page-header-row inverse">
	  Practicum
	</div>
	<LoaderAnimation visible={this.state.submittingResult}/>

	<h3>The Guest Experience</h3>
	<ul>
	  <li>At Costa Vida the Cashier position is critical to how each of our guests remembers their visit.</li>
	  <li>The Cashier in many cases is the last team member to engage with the guest.</li>
	  <li>A great smile and keen knowledge of our products is essential to the role of Cashier.</li>
	  <li>The ways in which the Cashier position helps are as follows:</li>
	  <li>Being quick to greet each guest.</li>
	  <li>Knowing the menu items and how to ring in all orders.</li>
	  <li>Offering suggestions to complete each meal (drinks, desserts).</li>
	</ul>
	<div className="row buttons-row">
	  <button className="btn btn-default" onClick={this.passWasClicked}>Pass</button>
	  <button className="btn btn-default" onClick={this.failWasClicked}>Fail</button>
	</div>
      </div>
    );
  }
}
