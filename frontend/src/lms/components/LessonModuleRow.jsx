import StaticImage from 'StaticImage';
import React, { PropTypes } from 'react';
import { Link } from 'react-router';

import { prop } from 'phaceologyUtil';
import urls, { history } from 'lmsUrls.js';

/** Renders a row in the lesson category list.
 prop  module The LessonModule object to render. Optional if isHeader is true.
 */
export default function LessonModuleRow({ module }) {
  return (
    <div className="row lesson-module">
      <Link to={urls.lessonList(module.id)}>
	<div className="col-xs-7 col-md-10">{prop(module, 'name', "[N/A]")}</div>
	<div className="col-xs-4 col-md-1 lesson-module-percent">{ module.percentComplete }</div>
	<div className="col-xs-1 col-md-1 lesson-module-percent">
	  <StaticImage className="lesson-module-arrow" src="whitearrow.svg" alt="More"/>
	</div>
      </Link>
    </div>
  );
}

LessonModuleRow.propTypes = {
  module:PropTypes.object.isRequired
};

