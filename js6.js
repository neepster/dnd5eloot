// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
// nav/search_index.js
//
// copyright (c) 2018-2021 drow <drow@bin.sh>
// all rights reserved

// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
// iife factory

((gc,fn) => fn(gc))(window, (global) => {

// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
// configuration

  let sel_idx = -1;

// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
// initialize search index

  document.observe('dom:loaded', () => {
    clear_search_index();
    $('index_query').observe('keyup',search_index);
  });
  document.observe('click', () => {
    clear_search_index();
  });

// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
// mousetrap

  if (Mousetrap) {
    Mousetrap.bind('/', (event) => {
      event.stop();
      clear_search_index();
      $('index_query').focus();
    });
  }

// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
// clear search index

  function clear_search_index () {
    $('index_query').setValue('');
    $('index_results').update('').hide();
  }

// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
// search index

  function search_index (event) {
    let query = $('index_query').getValue();
    let lead = new RegExp(`^${query}`,'i');
    let partial = new RegExp(query,'i');
    let list = [];

    Object.keys(site_index).forEach(title => {
      let score = 0; if (lead.test(title)) {
        score = ((query.length / title.length) * 10);
      } else if (partial.test(title)) {
        score = (query.length / title.length);
      }
      if (score > 0) {
        list.push({
          'title':      title,
          'url':        site_index[title],
          'score':      score,
          'title_lc':   title.toLowerCase
        });
      }
    });
    if (list.length > 0) {
      list.sort((a,b) => {
        return (a.score > b.score) ? -1
             : (a.score < b.score) ?  1
             : (a.title_lc > b.title_lc) ?  1
             : (a.title_lc < b.title_lc) ? -1
             : 0;
      });
      if (list.length > 10) {
        list = list.slice(0,10);
      }
      if (event.code == 'ArrowDown') {
        sel_idx = Math.min((sel_idx + 1),(list.length - 1));
        render_results(list);
      } else if (event.code == 'ArrowUp') {
        sel_idx = Math.max((sel_idx - 1),0);
        render_results(list);
      } else if (event.code == 'Enter') {
        if (sel_idx == -1) {
          window.location.assign(list[0]['url']);
        } else {
          window.location.assign(list[sel_idx]['url']);
        }
        clear_search_index();
      } else {
        sel_idx = -1;
        render_results(list);
      }
    } else {
      $('index_results').update('').hide();
    }
    event.preventDefault();
  }

// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
// render results list

  function render_results (list) {
    let ul = Builder.node('ul');

    if (sel_idx >= 0 && sel_idx < list.length) {
      list[sel_idx]['selected'] = true;
    }
    list.forEach(match => {
      let link = render_link(match);
      let item = render_item(match,link);

      ul.insert(item);
    });
    $('index_results').update(ul).show();
  }
  function render_link (match) {
    let attr = { 'href': match.url };
    return Builder.node('a',attr,match.title);
  }
  function render_item (match, link) {
    let attr = {};

    if (match.selected) {
      attr['class'] = 'selected';
    }
    return Builder.node('li',attr,link);
  }

// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
});
