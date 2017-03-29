import React, { PropTypes } from 'react';

import { prop } from 'phaceologyUtil';

import LessonModuleRow from 'LessonModuleRow';

/** Renders a row in the lesson category list.
 prop  category The LessonModuleCategory object to render. Optional if isHeader is true.
 prop  isHeader True if this is the header row.
 */
export default function LessonModuleCategoryRow({ category=null }) {
  const modules = prop(category, 'modules');
  return (
    <div style={{position:'relative'}}>
      <div className="row lesson-module-category">
	<div className="col-xs-7 col-md-9 lesson-module-category-name">{prop(category, 'name', 'FoH')}</div>
	<div className="col-xs-5 col-md-3 lesson-module-category-percent">% Complete</div>
      </div>
      { modules.map((module) => <LessonModuleRow module={module} key={module.id}/> )}
    </div>
  );
}

LessonModuleCategoryRow.propTypes = {
  category:PropTypes.object
};

