import React from 'react';
import { Link } from 'react-router';

import Button from 'react-bootstrap/lib/Button';
import ControlLabel from 'react-bootstrap/lib/ControlLabel';
import FormControl from 'react-bootstrap/lib/FormControl';
import FormGroup from 'react-bootstrap/lib/FormGroup';
import Modal from 'react-bootstrap/lib/Modal';

import UserLink from 'UserLink';
import urls from 'urls';
import models from 'models';
import { prop } from 'phaceologyUtil';

/* ES: TODO: Completely scratch this file and rewrite it when we have the final
 * designs, if that ever happens.
 */


/** Dialog to require a user to take a lesson.

 prop lessons An array of all available lessons.
 prop user The user object

 prop show Whether this should show.

 prop onClickCancel Callback for when cancel is clicked.
 prop onClickOk Callback for when OK is clicked. Parameter is the lesson.
 */
class RequireLessonModal extends React.Component {

  constructor(props) {
    super(props);
    this.state = {
      selectedIndex:-1
    };
    this.handleLessonSelected = this.handleLessonSelected.bind(this);
    this.handleClickOk = this.handleClickOk.bind(this);
  }

  getSelectedLesson() {
    return this.props.lessons[this.state.selectedIndex];
  }

  handleLessonSelected(event) {
    this.setState({ selectedIndex: event.target.value });
  }

  handleClickOk(event) {
    if (this.state.selectedIndex >= 0) {
      this.props.onClickOk(this.getSelectedLesson(), event);
    }
  }

  render() {
    const options = Array.concat([<option disabled hidden value={-1} key={-1}> -- select an option -- </option>],
                                 this.props.lessons.map((lesson, index) =>
                                                        <option value={ index } key={index} >{ prop(lesson, 'name') }</option>
                                                       )
                                );
                                        
    
    return (
      <Modal show={this.props.show}>
        <Modal.Header closeButton>
          <Modal.Title>Request Training</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <form>
            <FormGroup>
              <ControlLabel>Select a lesson</ControlLabel>
              <FormControl componentClass="select"
                           placeholder="select"
                           value={this.state.selectedIndex}
                           onChange={ this.handleLessonSelected }>
                { options }
              </FormControl>
            </FormGroup>
          </form>
          <p>{ prop(this.props.user, 'name') } will be sent a notification.</p>
        </Modal.Body>
        <Modal.Footer>
          <Button bsStyle="success"
                  onClick={this.handleClickOk}
                  disabled={this.state.selectedIndex===-1}>OK</Button>
          <Button onClick={this.props.onClickCancel}>Cancel</Button>
        </Modal.Footer>
      </Modal>
    );
  }
}

/** Dialog to require a user to take a lesson.

 prop lessons An array of all available lessons.
 prop user The user object

 prop show Whether this should show.

 prop onClickCancel Callback for when cancel is clicked.
 prop onClickOk Callback for when OK is clicked. Parameters are the lesson and score.
 */
class ManualLessonScoreModal extends React.Component {

  constructor(props) {
    super(props);
    this.state = {
      selectedIndex:-1,
      score:null
    };
    this.handleLessonSelected = this.handleLessonSelected.bind(this);
    this.handleClickOk = this.handleClickOk.bind(this);
    this.handleScoreChange = this.handleScoreChange.bind(this);
  }

  getSelectedLesson() {
    return this.props.lessons[this.state.selectedIndex];
  }

  handleLessonSelected(event) {
    this.setState({ selectedIndex: event.target.value });
  }

  handleClickOk(event) {
    if (this.state.selectedIndex >= 0) {
      this.props.onClickOk(this.getSelectedLesson(), this.state.score, event);
    }
  }

  handleScoreChange(event) {
    this.setState({ score: event.target.value });
  }

  isValid() {
    return (this.state.score >= 0 && this.state.score <= 100 && this.state.selectedIndex != -1);
  }
  
  getValidationState() {
    if (this.isValid()) {
      return 'success';
    } else {
      return 'error';
    }
  }

  render() {
    const options = Array.concat([<option disabled hidden value={-1} key={-1}> -- select an option -- </option>],
                                 this.props.lessons.map((lesson, index) =>
                                                        <option value={ index } key={index}>{ prop(lesson, 'name') }</option>
                                                    )
                                );
                                        
    
    return (
      <Modal show={this.props.show}>
        <Modal.Header closeButton>
          <Modal.Title>Request Training</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <form>
            <FormGroup validationState={this.getValidationState()}>
              <ControlLabel>Select a lesson</ControlLabel>
              <FormControl componentClass="select"
                           placeholder="select"
                           value={this.state.selectedIndex}
                           onChange={ this.handleLessonSelected }>
                { options }
              </FormControl>
              <ControlLabel>Score</ControlLabel>
              <FormControl type="number"
                           placeholder="0 to 100"
                           onChange={ this.handleScoreChange }/>
            </FormGroup>
          </form>
          <p>{ prop(this.props.user, 'name') } will be sent a notification.</p>
        </Modal.Body>
        <Modal.Footer>
          <Button bsStyle="success"
                  onClick={this.handleClickOk}
                  disabled={!this.isValid()}>OK</Button>
          <Button onClick={this.props.onClickCancel}>Cancel</Button>
        </Modal.Footer>
      </Modal>
    );
  }
}

/** A row of buttons for things you can do to a user.

 Property onNewLessonRequest A callback for when a new LessonRequest is
 created. Takes two parameters: the new LessonRequest pointer and the lesson.

 Prop user The User object.
 Prop lessons All available lessons
 Prop onNewLessonRequest Callback called when a new LessonRequest is created.
 Prop onNewQuizAttempt Callbacked called when a new QuizAttempt is created.
 */
class UserActions extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      showRequireLessonModal:false,
      showManaulLessonScoreModal:false,
      showDeleteModal:false
    };
    this.closeRequireLessonModal = this.closeRequireLessonModal.bind(this);
    this.openRequireLessonModal = this.openRequireLessonModal.bind(this);
    this.handleRequireLessonClickOk = this.handleRequireLessonClickOk.bind(this);

    this.closeManualLessonScoreModal = this.closeManualLessonScoreModal.bind(this);
    this.openManualLessonScoreModal = this.openManualLessonScoreModal.bind(this);
    this.handleManualLessonScoreClickOk = this.handleManualLessonScoreClickOk.bind(this);
  }

  handleRequireLessonClickOk(lesson, event) {
    console.log('require lesson ', lesson, ' for user ', this.props.user);
    let lr = new models.LessonRequest();
    lr.set('user', this.props.user);
    lr.set('created_by', models.User.current());
    lr.set('lesson', lesson);
    lr.save()
      .then((obj) => {
        this.closeRequireLessonModal();
        this.props.onNewLessonRequest(obj, lesson);
      })
      .fail((obj, error) => {
        // TODO: Fill in.
        console.error('Failed to save LessonRequest: ', error);
      });
  }

  closeRequireLessonModal() {
    this.setState({ showRequireLessonModal: false });
  }

  openRequireLessonModal() {
    this.setState({ showRequireLessonModal: true });
  }

  handleManualLessonScoreClickOk(lesson, score, event) {
    console.log('manual score ', score, ' for lesson ', lesson, ' for user ', this.props.user);

    new models.QuizAttempt()
      .set('user', this.props.user)
      .set('created_by', models.User.current())
      .set('lesson', lesson)
      .set('score', score)
      .save()
      .then((obj) => {
        this.closeManualLessonScoreModal();
        this.props.onNewQuizAttempt(obj, lesson, score);
      })
      .fail((obj, error) => {
        // TODO: Fill in.
        console.error('Failed to save QuizAttempt: ', error);
      });
  }

  closeManualLessonScoreModal() {
    this.setState({ showManualLessonScoreModal: false });
  }

  openManualLessonScoreModal() {
    console.log('openManualLessonScoreModal');
    this.setState({ showManualLessonScoreModal: true });
  }

  render() {
    if (!this.props.user) {
      return null;
    }


    return (
      <div className="container">
        <div className="row">
          <button type="button" className="btn btn-primary" onClick={this.openRequireLessonModal}>
            Request Traning
          </button>
          {' '}
          <button type="button" className="btn btn-primary" onClick={this.openManualLessonScoreModal}>Enter Lesson Score</button>
          {' '}
          <button type="button" className="btn btn-danger pull-right">Delete { prop(this.props.user, 'name') }</button>
        </div>

        <RequireLessonModal user={this.props.user}
                            lessons={this.props.lessons}
                            show={this.state.showRequireLessonModal}
                            onClickOk={this.handleRequireLessonClickOk}
                            onClickCancel={this.closeRequireLessonModal} />
        
        <ManualLessonScoreModal user={this.props.user}
                                lessons={this.props.lessons}
                                show={this.state.showManualLessonScoreModal}
                                onClickOk={this.handleManualLessonScoreClickOk}
                                onClickCancel={this.closeManaulLessonScoreModal} />
      </div>
    );
  }
}

/** One row in a score table (performance or lesson scores). */
class ScoreRow extends React.Component {
  renderHeader() {
    return (
      <tr>
        <th>{ this.props.categoryHeader }</th>
        <th>Score</th>
        <th>Date/Time</th>
        <th>Created By</th>
      </tr>
    );
  }


  renderRow() {
    const score = this.props.score;
    return (
      <tr>
        <td>{ prop(score, this.props.categoryField + '.name', 'N/A') }</td>
        <td>{ prop(score, 'score', 'N/A') }</td>
        <td>{ '' + score.createdAt }</td>
        <td><UserLink user={models.prop(score, 'created_by')}></UserLink></td>
      </tr>
    );
  }

  render() {
    if (this.props.isheader) {
      return this.renderHeader();
    } else {
      return this.renderRow();
    }
  }
}


/** A score table (performance or lesson scores). */
class ScoreList extends React.Component {
  render() {
    const rows = this.props.data.map((score) =>
                                     <ScoreRow score={ score } categoryField={ this.props.categoryField } key={ 'score-' + this.props.modelName + '-' + score.id } />
                                    );
    
    return (
      <div className="container">
        <h1>{ this.props.data.length } { this.props.header }</h1>
        <table className="table table-striped table-hover">
          <thead>
            <ScoreRow isheader={ true } categoryHeader={ this.props.categoryHeader } />
          </thead>
          <tbody>
            { rows }
          </tbody>
        </table>
      </div>
    );
  }
}

/** List of lesson requests for this user.

 Prop lessonRequests Array of LessonRequest objects to list.
 */
class LessonRequestList extends React.Component {
  render() {
    const rows = this.props.lessonRequests.map((lr, index) => <div className="row text-success center-block" key={index}>
                                               <span className="glyphicon glyphicon-flag" aria-hidden="true"/>
                                               On
                                               { ' ' + lr.createdAt },
                                               {' '}
                                               { userLink(prop(lr, 'created_by')) }
                                               {' '} requested user take Lesson:
                                               {' '}
                                               <span className="text-primary">
                                               { prop(lr, 'lesson.name') }
                                               </span>.
                                               </div>
                                              );
    return (
      <div className="container">
        { rows }
      </div>
    );
  }
}

/** User Detail screen

 Prop params.userId The ID of the User object.
 */
class UserDetail extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      user:null,
      lessonRequests:[],
      quizAttempts:[],
      performanceScores:[],
      lessons:[]
    };
    this.fetchLessonRequests = this.fetchLessonRequests.bind(this);
    this.fetchQuizAttempts = this.fetchQuizAttempts.bind(this);
  }
  
  componentDidMount () {
    // Fetch data initially
    // ES: Much of this can be extracted into a base class to save code.
    this.ignoreLastFetch = false;
    this.fetchData();
  }

  componentDidUpdate (prevProps) {
    // Respond to parameter change.
    if (prevProps.params.userId !== this.props.params.userId) {
      this.fetchData();
    }
  }

  componentWillUnmount () {
    // Ignore an inflight request.
    this.ignoreLastFetch = true;
  }

  fetchData () {
    this.fetchUser();
    this.fetchLessonRequests();
    this.fetchQuizAttempts();
    this.fetchPerformanceScores();
    this.fetchLessons();
  }

  fetchUser() {
    new models.Query('User').
      equalTo('id', this.props.params.userId).
      include('division').
      limit(1).
      find().then((results) => {
        if (!this.ignoreLastFetch) {
          this.setState({ user: results[0] });
        }
      }).fail((error) => {
        // TODO: Fill in.
        console.error('Error fetching users :', error);
      });
  }

  fetchLessonRequests() {
    console.log('fetchLessonRequests for user ', this.props.params.userId);
    new models.Query('LessonRequest').
      equalTo('user_id', this.props.params.userId).
      include('lesson').
      include('created_by').
      descending('created_at').
      find().then((results) => {
        if (!this.ignoreLastFetch) {
          this.setState({ lessonRequests: results });
        }
      }).fail((error) => {
        // TODO: Fill in.
        console.error('Error fetching data :', error);
      });
  }

  fetchQuizAttempts() {
    console.log('fetchQuizAttempts for user ', this.props.params.userId);
    
    new models.Query('QuizAttempt').
      equalTo('user_id', this.props.params.userId).
      include('lesson').
      include('created_by').
      descending('created_at').
      find().then((results) => {
        if (!this.ignoreLastFetch) {
          this.setState({ quizAttempts: results });
        }
      }).fail((error) => {
        // TODO: Fill in.
        console.error('Error fetching data :', error);
      });
  }

  fetchPerformanceScores() {
    console.log('fetchPerformanceScores for user ', this.props.params.userId);
    
    new models.Query('PerformanceScore').
      equalTo('user_id', this.props.params.userId).
      include('metric').
      include('created_by').
      descending('created_at').
      find().then((results) => {
        if (!this.ignoreLastFetch) {
          this.setState({ performanceScores: results });
        }
      }).fail((error) => {
        // TODO: Fill in.
        console.error('Error fetching data :', error);
      });
  }

  fetchLessons() {
    let q = new models.Query('Lesson');
    q.find().then((results) => {
        this.setState({ lessons: results });
    }).fail((error) => {
      // TODO: Fill in.
      console.error('Error fetching data :', error);
    });
  }

  userVal(key, def=null) {
    return this.state.user ? this.state.user.get(key) : def;
  }

  render () {

    const user = this.state.user;
    const name = this.userVal('name', '<None>');
    const pic =  this.userVal('profile_picture', '');
    const email =  this.userVal('email', '<None>');
    const division = user ? user.get('division') : null;
    const divisionName = division ? division.get('name') : '<None>';
    return (
      <div>
        <div className="container">
          <h1><Link to={urls.userList}>&laquo;&laquo;&laquo;</Link>{ name }</h1>
          <div className="row">
            <div className="col-md-4">
              <img src={ pic }/>
            </div>
            <div className="col-md-4">
              Division: { divisionName }
            </div>
            <div className="col-md-4">
              Email: <a href={ "mailto:" + email }>{ email }</a>
            </div>
          </div>
        </div>
        <UserActions user={ user }
                     lessons={this.state.lessons}
                     onNewLessonRequest={this.fetchLessonRequests}
                     onNewQuizAttempt={this.fetchQuizAttempts}
                     />
        <LessonRequestList lessonRequests={this.state.lessonRequests}/>
        <ScoreList user={ user } categoryField="metric" categoryHeader="Metric" header="Performance Scores" data={this.state.performanceScores} />
        <ScoreList user={ user } categoryField="lesson" categoryHeader="Lesson" header="Lesson Scores" data={this.state.quizAttempts} />
      </div>
    );
  }
}

module.exports = UserDetail;
