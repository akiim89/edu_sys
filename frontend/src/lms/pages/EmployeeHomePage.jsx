import React, { PropTypes } from 'react';

import { prop } from 'phaceologyUtil';
import models from '../../models.js';
import urls from '../lmsUrls.js';

import EmployeeSummary from '../components/EmployeeSummary.jsx';
import LessonModuleCategoryList from '../components/LessonModuleCategoryList.jsx';

export default class QuizDetailPage extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      categories:[]
    };
  }

  componentDidMount () {
    // Fetch data initially
    this.ignoreLastFetch = false;
    this.fetchData();
  }

  componentDidUpdate (prevProps) {
    // Respond to parameter change.
    // NOTE: No parameters for now. Other classes might need this, or we might need it later.
  }

  componentWillUnmount () {
    // Ignore an inflight request.
    this.ignoreLastFetch = true;
  }

  fetchData () {
    new models.Query('LessonModuleCategory')
      .include('module,module.lesson')
      .find()
      .then((results) => {
	this.setState({ categories: results });
      }).fail((error) => {
	// TODO: Fill in.
	console.error('Error fetching data:', error);
	if (error.code === 119) { // Forbidden. We must not be logged in.
          models.User.logOut().then((user) => {
            urls.gotoHome();
          });
	}
      });
  }
  
  render () {
    return ( <div>
	     <EmployeeSummary/>
	     <LessonModuleCategoryList categores={this.state.categories} />
	     </div>
    );
  }
}
