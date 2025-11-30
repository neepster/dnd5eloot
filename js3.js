// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
// ux/dark_mode.js
//
// copyright (c) 2020-2021 drow <drow@bin.sh>
// all rights reserved

// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
// iife factory

((gc,fn) => fn(gc))(window, (global) => {

// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
// configuration

  let toggle_button = false;

// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
// dark mode

  document.observe('dom:loaded', () => {
    toggle_button = $('toggle_dark_mode');

    if (get_cookie('dark_mode')) {
      enable_dark_mode();
    }
    if (toggle_button) {
      toggle_button.observe('click',toggle_dark_mode);
    }
  });

// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
// toggle dark mode

  function toggle_dark_mode (event) {
    event.stop();

    if (get_cookie('dark_mode')) {
      disable_dark_mode();
      delete_cookie('dark_mode');
    } else {
      enable_dark_mode();
      persistent_cookie('dark_mode',1);
    }
  }
  global.toggle_dark_mode = toggle_dark_mode;

// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
// enable dark mode

  function enable_dark_mode () {
    $$('body').forEach(e => e.addClassName('dark_mode'));

    if (toggle_button) {
      toggle_button.value = 'Undark Mode'
    }
  }
  global.enable_dark_mode = enable_dark_mode;

// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
// disable dark mode

  function disable_dark_mode () {
    $$('body').forEach(e => e.removeClassName('dark_mode'));

    if (toggle_button) {
      toggle_button.value = 'Dark Mode'
    }
  }
  global.disable_dark_mode = disable_dark_mode;

// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
});
