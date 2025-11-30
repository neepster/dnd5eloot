// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
// tk/cookie.js
//
// copyright (c) 2006-2021 drow <drow@bin.sh>
// all rights reserved

// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
// iife factory

((gc,fn) => fn(gc))(window, (global) => {

// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
// configuration

  let default_opts = {
    'domain':   '.bin.sh',
    'path':     '/',
    'secure':   true
  };
  let forthwith = cookie_date(2000,1,1,0,0,0);
  let never = cookie_date(2037,1,1,0,0,0);
  let vault = {};

// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
// cookie options

  let opt_steps = [
    { 'key': 'expires', 'fn': (date) => {
      if (date === 'now') {
        date = forthwith;
      } else if (date === 'never') {
        date = never;
      }
      return 'expires=' + date.toUTCString();
    }},
    { 'key': 'domain', 'fn': (value) => `domain=${value}` },
    { 'key': 'path',   'fn': (value) => `path=${value}` },
    { 'key': 'secure', 'fn': (value) => 'secure' }
  ];

// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
// load cookies

  function load_cookies () {
    document.cookie.split('; ').forEach(cookie => {
      let list = cookie.split('=');
      let key = list[0];
      let value = decodeURIComponent(list[1]);

      if (match = /^json:(.+)/.exec(value)) {
        value = JSON.parse(match[1]);
      }
      vault[key] = value;
    });
  }
  load_cookies();

// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
// get cookie

  function get_cookie (key) {
    if (key) {
      return vault[key];
    } else {
      return vault;
    }
  }
  global.get_cookie = get_cookie;

// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
// set cookie

  function set_cookie (key, value, opts) {
    vault[key] = value;

    if (typeof(value) == 'string') {
      value = encodeURIComponent(value);
    } else {
      value = 'json:' + encodeURIComponent(JSON.stringify(value));
    }
    let list = [ `${key}=${value}` ];

    opt_steps.forEach(step => {
      let value; if (value = opts[step.key]) {
        list.push(step.fn(value));
      } else if (value = default_opts[step.key]) {
        list.push(step.fn(value));
      }
    });
    document.cookie = list.join('; ');
  }
  global.set_cookie = set_cookie;

// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
// persistent cookie

  function persistent_cookie (key, value, opts) {
    if (opts) {
      opts.expires = never;
    } else {
      opts = { 'expires': never };
    }
    return set_cookie(key,value,opts);
  }
  global.persistent_cookie = persistent_cookie;

// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
// persistent chip

  function set_cookie_chip (key, chip, value, opts) {
    let cookie; if (vault[key]) {
      cookie = vault[key];
    } else {
      cookie = {};
    }
    cookie[chip] = value;
    return persistent_cookie(key,cookie,opts);
  }
  global.set_cookie_chip = set_cookie_chip;

// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
// delete cookie

  function delete_cookie (key, opts) {
    if (vault[key]) {
      delete vault[key];

      if (opts) {
        opts.expires = forthwith;
      } else {
        opts = { 'expires': forthwith };
      }
      set_cookie(key,'',opts);
    }
  }
  global.delete_cookie = delete_cookie;

// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
// construct date

  function cookie_date (y,m,d,h,n,s) {
    let then = new Date(y,m,d,h,n,s);
    return fix_time(then);
  }
  function cookie_days (d) {
    let then = new Date();
    let t = then.getTime() + (d * 86400 * 1000);

    then.setTime(t);
    return fix_time(then);
  }
  function fix_time (then) {
    let base = new Date(0);
    let skew = base.getTime();

    if (skew > 0) {
      then.setTime(then.getTime() - skew);
    }
    return then;
  }

// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
});
