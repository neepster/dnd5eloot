// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
// nav/sidebar.js
//
// copyright (c) 2013-2021 drow <drow@bin.sh>
// all rights reserved

// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
// iife factory

((gc,fn) => fn(gc))(window, (global) => {

// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
// configuration

  let default_nav = {
    '0db377921f4ce762c62526131097968f': 'show', // general
    'f8e19bfcbc718a84ee8ed8aae472f9e2': 'show', // fantasy
    '2bff9972bf9bd1a818caa7eaa4083dc3': 'show', // d&d 5e
  };
  let span_disclose = '<span class="disclose"></span>';
  let icon = { 'open': '&#x25be;', 'closed': '&#x25b8;' };

// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
// initialize sidebar nav

  document.observe('dom:loaded', () => {
    init_sidebar_nav();
  });
  function init_sidebar_nav () {
    let state = get_cookie('nav') || default_nav;
    let l = window.location;
    let page_href = `${l.protocol}//${l.hostname}${l.pathname}`;

    $$('.nav-section a').forEach(link => {
      if (link.href == page_href) {
        list_id = link.up('div.list').identify();
        state[list_id] = 'show';
      }
    });
    $$('.nav-section').forEach(section => {
      let nav_h2 = section.down('h2');
      let h2_id = nav_h2.identify();
      let h2_text = span_disclose + nav_h2.innerHTML;
          nav_h2.update(h2_text);
      let nav_list = section.down('div.list');
      let list_id = nav_list.identify();

      if (list_id == 'cff1be7f7b27cf1ec2e7be8bcc63df62') {
        disclose(nav_h2,'open');
      } else if (list_id == '317705e402a8529da72a44045db42bf3') {
        disclose(nav_h2,'open');
      } else {
        if (state[list_id] == 'show') {
          disclose(nav_h2,'open');
        } else {
          disclose(nav_h2,'closed');
          nav_list.hide();
        }
        $(h2_id).observe('click',toggle_section);
      }
    });
    $('nav-sidebar').show();
  }

// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
// toggle section

  function toggle_section (event) {
    if (nav_h2 = event.element()) {
      if (nav_list = nav_h2.next('div.list')) {
        let list_id = nav_list.identify();
        let len = nav_len(nav_list);
        let effect_opts = { 'duration': (0.05 * len) };

        if (nav_list.visible()) {
          disclose(nav_h2,'closed');
          Effect.SlideUp(list_id,effect_opts);
          set_cookie_chip('nav',list_id,'hide');
        } else {
          disclose(nav_h2,'open');
          Effect.SlideDown(list_id,effect_opts);
          set_cookie_chip('nav',list_id,'show');
        }
      }
    }
  }
  function nav_len (list) {
    return list.down('ul').descendants().length;
  }
  function disclose (h2, state) {
    h2.down('span.disclose').update(icon[state]);
  }

// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
});
