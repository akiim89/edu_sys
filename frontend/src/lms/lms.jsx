import './facebookLogin';

import React from 'react';
import ReactDOM from 'react-dom';

//import BootstrapCss from 'bootstrap/dist/css/bootstrap.css';

import { Router, Route, IndexRoute } from 'react-router';

import models from 'models';
import EmployeeNavbar from 'EmployeeNavbar';
import EmployeeMenu from 'EmployeeMenu';

import EmployeeLoginPage from 'EmployeeLoginPage';
import LessonModuleCategoryListPage from 'LessonModuleCategoryListPage';
import LessonListPage from 'LessonListPage';
import LessonDetailPage from 'LessonDetailPage';
import QuizDetailPage from 'QuizDetailPage';
import EmployeeSettingsPage from 'EmployeeSettingsPage';

import ReportsDivisionListPage from 'ReportsDivisionListPage';
import ReportsDivisionDetailPage from 'ReportsDivisionDetailPage';
import ReportsLessonDetailPage from 'ReportsLessonDetailPage';

import PracticumDivisionListPage from 'PracticumDivisionListPage';
import PracticumLessonDetailPage from 'PracticumLessonDetailPage';

import urls, { history } from 'lmsUrls.js';
import {addErrorHandler, handleError} from 'lmsUtil';

let routeChangeCallbacks = [];
function changeHandler(oldRoute, newRoute) {
  console.log('changeHandler ', oldRoute, ', ', newRoute);
  for (let cb of routeChangeCallbacks) {
    console.log('callback ', cb);
    cb(oldRoute, newRoute);
  }
}


class RootPage extends React.Component {

  constructor(props) {
    super(props);

    this.state = {
      menuVisible:false,
      errorMessageVisible:false,
      divisions:[]
    };
    this.toggleMenu = this.toggleMenu.bind(this);
    this.routeDidChange = this.routeDidChange.bind(this);

    routeChangeCallbacks.push(this.routeDidChange);
    addErrorHandler(this.errorHandler.bind(this));
    this.fetchData();
  }
  
  errorHandler(error) {
    this.setState({errorMessageVisible:true});
  }

  fetchData() {
    if (models.User.current()) {
      new models.Query(models.Division).find().then(divisions => {
	this.setState({divisions:divisions});
      }).fail((error) => {
	handleError(error);
      });
    }
  }

  toggleMenu() {
    this.setState((prevState, props) => {
      return {menuVisible: !prevState.menuVisible};
    });
  }

  routeDidChange(oldRoute, newRoute) {
    console.log('routeDidChange ', oldRoute, newRoute);
    this.setState({menuVisible:false});
    if (oldRoute.location.pathname === urls.home) {
      // Probably a login. Recheck for divisions.
      this.fetchData();
    }
  }

  render() {
    return (
      <div>
	<EmployeeNavbar onMenuClick={this.toggleMenu} />
	<EmployeeMenu visible={this.state.menuVisible} canViewReports={this.state.divisions.length > 0}/>
	{this.props.children}
      </div>
    );
  }
};

class App extends React.Component {
  constructor(props) {
    super(props);
  }
  
  render() {
    return (
      <Router history={history}>
	<Route path="/" component={RootPage} onChange={changeHandler}>
	  <IndexRoute component={EmployeeLoginPage} />
	  <Route path={urls.moduleList} component={LessonModuleCategoryListPage} />
	  <Route path={urls.settings} component={EmployeeSettingsPage}/>
	  <Route path={urls.lessonList()} component={LessonListPage} />
	  <Route path={urls.lessonDetail()} component={LessonDetailPage} />
	  <Route path={urls.quizDetail()} component={QuizDetailPage}/>

	  <Route path={urls.reportsDivisionList} component={ReportsDivisionListPage}/>
	  <Route path={urls.reportsDivisionDetail()} component={ReportsDivisionDetailPage}/>
	  <Route path={urls.reportsLessonDetail()} component={ReportsLessonDetailPage}/>

	  <Route path={urls.practicumDivisionList} component={PracticumDivisionListPage}/>
	  <Route path={urls.practicumLessonDetail()} component={PracticumLessonDetailPage}/>
	</Route>
      </Router>
    );
  }
};

ReactDOM.render(<App/>, document.getElementById('react-content'));

let learn = {models:models, history:history};
export default learn;
