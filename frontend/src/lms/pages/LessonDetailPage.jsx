import React from 'react';

import models from 'models';
import urls from 'lmsUrls';
import { prop } from 'phaceologyUtil';
import { Link } from 'react-router';
import { handleError } from 'lmsUtil';

import StaticImage from 'StaticImage';
import LoaderAnimation from 'LoaderAnimation';

export default class LessonDetailPage extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      lesson:null,
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
    console.log('LessonListPage: params ', this.props.params);
    new models.Query(models.Lesson).get(this.props.params.lessonId).then((lesson) => {
      this.setState({lesson:lesson, fetchInProgress:false});
    }).fail(handleError);
  }
  render () {
    let lessonId = this.props.params.lessonId;
    return (
      <div className="lesson-detail-page">
	<LoaderAnimation visible={this.state.fetchInProgress}/>
	<div className="video-wrapper">
	  <StaticImage alt="video" src="video.jpg" className="video"/>
	</div>
	<div className="row text-row">
	  <div className="col-xs-12 col-md-offset-3 col-md-6 text">
	    <h3>Action Items</h3>
	    <p>Review all menu items</p>
	    <ul>
	      <li>Using the Menu Build cards – review the build of each item.</li>
	      <li>Become familiar with what comes on each product.</li>
	      <li>Understand extra charges.</li>
	    </ul>
	  </div>
	</div>
	<div className="row button-area">
	  <Link className="btn btn-default" to={urls.quizDetail(lessonId)}>Take Quiz</Link>
	</div>
      </div>
    );
  }
}
