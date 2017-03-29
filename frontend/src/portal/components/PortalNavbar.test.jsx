import React from 'react';
import renderer from 'react-test-renderer';
import PortalNavbar from 'PortalNavbar';

test('navbar renders correctly', () => {
  const tree = renderer.create(
      <PortalNavbar />
  ).toJSON();
  expect(tree).toMatchSnapshot();
});

