import React from 'react';
import ReactDOM from 'react-dom';
import models from 'models';
import { urls } from 'lmsUrls';
import { handleError } from 'lmsUtil';
import { prop } from 'phaceologyUtil';

import StaticImage from 'StaticImage';
import LoaderAnimation from 'LoaderAnimation';
import { Link } from 'react-router';

function DivisionRow({division}) {
  return (
    <div className="row division inverse-linked-row inverse two-part-row">
      <Link to={urls.reportsDivisionDetail(division.id)}>
	<div className="col-xs-11">
	  <div className="row row-header">
	    {prop(division, 'name')}
	  </div>
	  <div className="row row-detail">
	    {prop(division, 'description')}
	  </div>
	</div>
	<div className="col-xs-1 arrow-col">
	  <StaticImage src="arrow.svg" alt="view" className="arrow"/>
	</div>
      </Link>
    </div>
  );
}

export default class ReportsDivisionListPage extends React.Component {
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
    new models.Query(models.Division)
      .find()
      .then((divisions) => {
	console.log('got divisions ', divisions);
	this.setState({divisions:divisions, fetchInProgress:false});
      }).fail(handleError);
  }

  render() {
    const waitingView = (
	<div className="reports-division-list-page">
	  <LoaderAnimation visible={true}/>
	</div>
      );

    if (this.state.fetchInProgress ) {
      return waitingView;
    }

    return (
      <div className="container reports-division-list-page">
	<div className="row page-header-row inverse">
	  Reports
	</div>
	{ this.state.divisions.map(division => <DivisionRow division={division} key={division.id}/>) }
      </div>
    );
  }
}
