/// A handy function to look up a property on a Parse object. Like calling
/// obj.get(propPath) except it doesn't blow up if obj is null or undefined. As
/// a bonus, propPath can be a dotted path. So you can do something like:
///
/// prop(user, 'division.name');
///
/// to get the name of the user's division. It's like user.get('division').get('name')
/// plus null safety.
export function prop(obj, propPath, defValue=undefined) {
  if (!obj) {
    return defValue;
  }
  let parts = propPath.split('.');
  let ret = obj;
  for (let p of parts) {
    try {
      ret = ret.get(p);
    } catch(e) {
      console.warn('prop: could not get part ', p);
      return defValue;
    }
    if (!ret) {
      return defValue;
    }
  }
  return ret;
}


export function setupUrls(urls, history) {
  function makeGoto(path) {
    return function(...params) {
      if (typeof(path) === 'function') {
        history.push(path(...params));
      } else {
        history.push(path);
      }
    };
  };

  for (let k in urls) {
    if (urls.hasOwnProperty(k)) {
      let fnName = 'goto' + k.charAt(0).toUpperCase() + k.slice(1);
      urls[fnName] = makeGoto(urls[k]);

      if (k.indexOf(':') !== -1) {
        let makerFnName = 'linkTo' + fnName.slice(4);
        urls[makerFnName] = makeLinker(urls[k]);
      }
    }
  }
}

export default { prop:prop, setupUrls:setupUrls };
