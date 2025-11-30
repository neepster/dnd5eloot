// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
// common.js
//
// copyright (c) 2018-2021 drow <drow@bin.sh>
// all rights reserved

// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
// iife factory

((gc,fn) => fn(gc))(window, (global) => {

// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
// extend functions

  (() => {
    let list = {};

    function extend_fn (key, fn) {
      if (list[key]) {
        list[key].push(fn);
      } else {
        list[key] = [fn];
      }
    }
    global.extend_fn = extend_fn;

    function run_extensions (key, args) {
      let l; if (l = list[key]) {
        l.forEach(fn => fn(args));
      }
    }
    global.run_extensions = run_extensions;
  })();

// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
// random

  function rand (x, z = 0) { return Math.floor(Math.random() * x) + z; }
  global.rand = rand;

  function rand_seed () { return rand(2147483647); }
  global.rand_seed = rand_seed;

  function rand_index (s) { return rand($(s).options.length); }
  global.rand_index = rand_index;

// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
// shuffle array, durstenfeld

  Object.extend (Array.prototype, {
    'shuffle': () => {
      let idx; for (idx = this.length - 1; idx > 0; idx--) {
        let rdx = rand(idx + 1);
        let swap = this[idx]; this[idx] = this[rdx]; this[rdx] = swap;
      }
      return this;
    }
  });

// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
// templates

  function init_fmt (proto) {
    let fmt = {}; Object.keys(proto).forEach(key => {
      fmt[key] = new Template(proto[key]);
    });
    return {
      'add': (key, string) => { fmt[key] = new Template(string); },
      'copy': (src, key) => { fmt[key] = fmt[src]; },
      'eval': (key, values) => { return fmt[key].evaluate(values); }
    };
  }
  global.init_fmt = init_fmt;

// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
// kill submit events on scripted forms

  document.observe('dom:loaded', () => {
    $$('form.scripted').forEach(form => {
      $(form).observe('submit', event => event.stop());
    });
  });

// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
// select children

  function select_children (parent, desc) {
    return parent.childElements().grep(new Selector(desc));
  }
  global.select_children = select_children;

// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
// query string from object

  function build_query (object) {
    let query = new URLSearchParams();

    Object.keys(object).forEach(key => {
      query.set(key,object[key]);
    });
    return query.toString();
  }
  global.build_query = build_query;

// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
// construct json download href

  function download_json (json) {
    return 'data:text/json;charset=utf-8,' + encodeURIComponent(json);
  }
  global.download_json = download_json;

// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
});
