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

function EmployeeRow({user}) {
  let role = 'Employee';
  try {
    let roles = prop(user, 'roles');
    console.log('roels ', roles);
    console.log('roles[0] ', roles[0]);
    role = prop(roles[0], 'name');
    console.log('role ', role);
  } catch (e) {
  }
  return (
    <div className="row employee inverse inverse-linked-row">
      <Link to={urls.reportsEmployeeDetail(user.id)}>
	<div className="col-xs-3">
	  <ProfilePic user={user}/>
	</div>
	<div className="col-xs-6">
	  <div className="row name">
	    {prop(user, 'name')}
	  </div>
	  <div className="row role">
	    {role}
	  </div>
	</div>
	<div className="col-xs-3 percent-complete">
	  100
	</div>
      </Link>
    </div>
  );
}

function LessonRow({lesson, divisionId}) {
  return (
    <div className="row ph-row lesson linked-row">
      <Link to={urls.reportsLessonDetail(divisionId, lesson.id)}>
	<div className="col-xs-9 name">{prop(lesson, 'name')}</div>
	<div className="col-xs-2 percent">75%</div>
	<ArrowCol alt="details"/>
      </Link>
    </div>
  );
}

export class ModuleRow extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      expanded:false
    };
    this.rowWasClicked = this.rowWasClicked.bind(this);
  }
  
  rowWasClicked(ev) {
    console.log('ModuleCategoryRow.rowWasClicked');
    this.setState((prevState) => ({expanded:!prevState.expanded}));
  }

  
  render() {
    const module = this.props.module;
    const lessons = prop(module, 'lessons');
    const divisionId = this.props.divisionId;
    
    if (this.state.expanded) {
      return (
	<div>
	  <div className="row module ph-row" onClick={this.rowWasClicked}>
	    <div className="col-xs-11 module-name">
	      {prop(module, 'name')}
	    </div>
	    <ArrowCol alt="collapse" expanded={true}/>
	  </div>
	  {lessons.map(lesson => <LessonRow divisionId={divisionId} lesson={lesson} key={lesson.id}/>)}
	</div>
      );
    } else {
      return (
	<div className="row inverse module ph-row" onClick={this.rowWasClicked}>
	  <div className="col-xs-11 module-name">
	    {prop(module, 'name')}
	  </div>
	  <ArrowCol alt="collapse" inverse={true}/>
	</div>
      );
    }
  }
}

/** ModuleCategoryRow
 * prop moduleCategory
 **/
export class ModuleCategoryRow extends React.Component {
  constructor(props) {
    super(props);
  }

  render() {
    const moduleRows = prop(this.props.moduleCategory, 'modules').map(m => <ModuleRow module={m} divisionId={this.props.divisionId} key={m.id}/>);
    return (
      <div className="module-category-container">
	<div className="row module-category">
	  <div className="col-xs-12 module-category-name">
	    {prop(this.props.moduleCategory, 'name')}
	  </div>
	</div>
	{moduleRows}
      </div>
    );
  }
}

export default class ReportsDivisionDetailPage extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      employees:[],
      moduleCategories:[],
      modulesSelected:false,
      fetchInProgress:true
    };

    this.selectModules = this.selectModules.bind(this);
    this.selectEmployees = this.selectEmployees.bind(this);
  }
  
  componentDidMount () {
    // Fetch data initially
    this.fetchData();
  }

  componentWillUnmount () {
    // Ignore an inflight request.
    this.ignoreLastFetch = true;
  }

  selectModules() {
    this.setState({modulesSelected:true});
  }
  
  selectEmployees() {
    this.setState({modulesSelected:false});
  }

  fetchData() {
    const employeesPromise = new models.Query(models.User)
	    .include('roles')
	    .equalTo('division_id', this.props.params.divisionId)
	    .find();
    const moduleCategoriesPromise = new models.Query(models.LessonModuleCategory)
	    .include('modules')
	    .include('modules.lessons')
	    .find();
    const divisionPromise = new models.Query(models.Division)
	    .get(this.props.params.divisionId);

    models.Parse.Promise.when([employeesPromise, moduleCategoriesPromise, divisionPromise]).then((results) => {
      this.setState({employees:results[0],
		     moduleCategories:results[1],
		     division:results[2],
		     fetchInProgress:false});
    }).fail(handleError);
  }

  render() {
    if (this.state.fetchInProgress ) {
      return (
	<div className="reports-division-list-page">
	  <LoaderAnimation visible={true}/>
	</div>
      );
    }

    if (this.state.modulesSelected) {
      return (
	<div className="container reports-division-detail-page">
    	  <div className="row page-header-row inverse">
    	    Reports
    	  </div>
	  <DivisionHeaderRow division={this.state.division}/>
	  <div className="row ph-row ph-tab-row">
	    <div className="col-xs-6 ph-gray" onClick={this.selectEmployees}>Employees</div>
	    <div className="col-xs-6">Modules</div>
	  </div>
	  { this.state.moduleCategories.map((c) => <ModuleCategoryRow moduleCategory={c} divisionId={this.props.params.divisionId} key={c.id}/>) }
	</div>
      );
    } else {
      return (
	<div className="container reports-division-detail-page">
    	  <div className="row page-header-row inverse">
    	    Reports
    	  </div>
	  <DivisionHeaderRow division={this.state.division}/>
	  <div className="row ph-row ph-tab-row">
	    <div className="col-xs-6">
	      Employees
	    </div>
	    <div className="col-xs-6 ph-gray" onClick={this.selectModules}>
	      Modules
	    </div>
	  </div>
	  <div>
	    <div className="row employees-header">
	      <div className="col-xs-offset-8 col-xs-4">
		% Complete
	      </div>
	    </div>
	    { this.state.employees.map((e) => <EmployeeRow user={e} key={e.id}/>) }
        </div>
      </div>
      );
    }
  }
}
