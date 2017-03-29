/*global setTimeout */

import React from 'react';

import models from 'models';
import urls from 'lmsUrls';
import { handleError } from 'lmsUtil';
import { prop } from 'phaceologyUtil';
import { Link } from 'react-router';

import StaticImage from 'StaticImage';
import LoaderAnimation from 'LoaderAnimation';

function ProgressBar() {
  return null;
}

function QuizAnswer({answer, isUnchosen, onClick}) {
  const className = 'col-xs-12 col-md-6 col-md-offset-3 answer' + ((isUnchosen) ? ' unchosen-answer' : '');
  return (
    <div className="row answer-row" onClick={onClick}>
      <div className={className}>
	{prop(answer, 'text')}
      </div>
    </div>
  );
}

function Announcement({style, children}) {
  if (style === 'hidden') {
    return (
      <div className="row announcement" style={{visibility:'hidden'}}>
	<div className="col-xs-12 announcement-col">
	  <span className={"label label-success"}>waiting...</span>
	</div>
      </div>
    );
  }
  return (
    <div className="row announcement">
      <div className="col-xs-12 announcement-col">
	<span className={"label label-" + style}>{children}</span>
      </div>
    </div>
  );
}

export default class QuizDetailPage extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      lesson:null,
      questionIndex:0,
      fetchInProgress:true,
      checkingAnswer:false,
      answerIsWrong:false,
      quizPassed:false
    };
    this.continueWasClicked = this.continueWasClicked.bind(this);
    this.nextCategoryWasClicked = this.nextCategoryWasClicked.bind(this);

    // The QuizAttempt object that gets created on the server when we submit the
    // first response.
    this.quizAttemptId = -1;
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
    new models.Query(models.Lesson)
      .include('questions')
      .include('questions.answers')
      .get(this.props.params.lessonId)
      .then((lesson) => {
	console.log('got lesson ', lesson);
	this.setState({lesson:lesson, fetchInProgress:false});
      }).fail(handleError);
  }

  nextCategoryWasClicked(ev) {
    urls.gotoLessonList(prop(this.state.lesson, 'module').id);
  }

  continueWasClicked(ev) {
    console.log('continueWasClicked');

    // If we're showing the answer check result:
    if (this.state.answerIsWrong || this.state.answerIsRight) {
      this.setState((prevState, props) => {
	return {questionIndex:prevState.questionIndex + 1,
		answerIsRight:false,
		answerIsWrong:false,
		chosenAnswer:null};
      });
    } else {

      if (!this.state.chosenAnswer) {
	console.log('continueWasClicked: No answer');
	return; // No answer chosen. Do nothing.
      }
      // Check if the answer is right.
      this.setState({checkingAnswer:true});
      models.Parse.Cloud.run('submitAnswer', { answerId: this.state.chosenAnswer.id, quizAttemptId:this.quizAttemptId })
	.then((result) => {
	  this.quizAttemptId = result.quizAttemptId;
	  console.log('Got result ', result);
	  if (result.isCorrect) {
	    this.setState({checkingAnswer:false,
			   answerIsRight:true});
	  } else {
	    this.setState({checkingAnswer:false,
			   answerIsWrong:true});
	  }
	}).fail(handleError);
    }
  }

  chooseAnswer(answer) {
    console.log('chooseAnswer: ', answer);
    if (this.state.answerIsWrong || this.state.answerIsRight) {
      // They already guessed on this one.
      return;
    }
    this.setState({chosenAnswer:answer});
  }


  render () {
    const waitingView = (
	<div className="quiz-detail-page">
	  <LoaderAnimation visible={true}/>
	</div>
      );

    if (this.state.fetchInProgress || this.state.finalCheckInProgress) {
      return waitingView;
    }

    const questions = prop(this.state.lesson, 'questions', []);

    if (this.state.questionIndex >= questions.length) {
      // Quiz is finished.
      if (this.state.quizFailed) {
	return (
	  <div className="quiz-detail-page container">
	    <div className="row">
	      <StaticImage className="lesson-failed" src="lesson-failed.jpg" alt="Lesson failed"/>
	    </div>
	    <div className="button-area row">
	      <input className="btn btn-default" type="button" value="Next Category" onClick={this.nextCategoryWasClicked} />
	    </div>
	  </div>
	);
	  
      } else if (this.state.quizPassed) {
	return (
	  <div className="quiz-detail-page container">
	    <div className="row lesson-passed-heading">
	      You did it!
	    </div>
	    <div className="row lesson-passed-image">
	      <StaticImage className="lesson-passed" src="completecat.svg" alt="Lesson passsed"/>
	    </div>
	    <div className="row lesson-passed-message-1">
	      You've completed
	    </div>
	    <div className="row lesson-passed-message-2">
	      {prop(this.state.lesson, 'name')}
	    </div>
	    <div className="button-area row">
	      <input className="btn btn-default" type="button" value="Next Category" onClick={this.nextCategoryWasClicked} />
	    </div>
	  </div>
	);
      } else {
	if (!this.finalCheckInProgress) {
	  this.finalCheckInProgress = true;
	  // ES: Fill in a real check.
	  console.log('asetting timeout ', this);
	  setTimeout(() => {
	    console.log('asetting quiz passed ', this);
	    this.setState({quizPassed:true});
	    this.finalCheckInProgress = false;
	  }, 1000);
	}
	return waitingView;
      }
    }

    const question = questions[this.state.questionIndex];
    const answers = prop(question, 'answers');
    const answerRows = answers.map(a =>
				   <QuizAnswer answer={a}
				   isUnchosen={this.state.chosenAnswer && a !== this.state.chosenAnswer}
				   key={a.id}
				   onClick={() => this.chooseAnswer(a)}/>
				  );

    let announcement = null;
    if (this.state.answerIsRight) {
      announcement = <Announcement style="success"><b>Congrats!</b> You got it!</Announcement>;
    } else if (this.state.answerIsWrong) {
      announcement = <Announcement style="default"><b>Sorry!</b> That's incorrect.</Announcement>;
    } else {
      announcement = <Announcement style="hidden"/>;
    }

    return (
      <div className="quiz-detail-page container">
	<LoaderAnimation visible={this.state.checkingAnswer}/>
	<div className="row header">
	  <div className="col-xs-12">
	    {prop(this.state.lesson, 'name')} Quiz
	  </div>
	</div>
	<ProgressBar on={this.state.questionIndex} of={questions.length}/>
	<div className="row question">
	  <div className="col-xs-12">
	    {prop(question, 'text')}
	  </div>
	</div>
	{answerRows}
	{announcement}
	<div className="button-area row">
	  <input className="btn btn-default" type="button" value="Continue" onClick={this.continueWasClicked} />
	</div>
      </div>
    );
  }
}
