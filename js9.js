// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
// dice/control.js
//
// copyright (c) 2009-2021 drow <drow@bin.sh>
// all rights reserved

// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
// iife factory

((gc,fn) => fn(gc))(window, (global) => {

// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
// initialize component

  document.observe('dom:loaded', () => {
    new_dice();

    $('dice_form').observe('submit',new_dice);
    $('dice_string').observe('change',new_dice);
    $('roll_dice').observe('click',new_dice);
  });

// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
// roll dice

  function new_dice () {
    let string = $('dice_string').getValue();
    let result;

    let match; if (match = /^(\d+) x (.+)/.exec(string)) {
      result = multi_dice(match[1],match[2]);
    } else {
      result = roll_dice_det(string);
    }
    let dice_out = [ '.', '..', '...', result ];
    let out_div = $('dice_result');

    function dice_result () {
      if (dice_out.length) {
        out_div.update(dice_out.shift());

        if (dice_out.length) {
          setTimeout(dice_result,100);
        }
      }
    }
    setTimeout(dice_result,100);
  }

// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
// multi-dice

  function multi_dice (n, string) {
    let list = [];

    let i; for (i = 0; i < n; i++) {
      list.push(roll_dice_det(string));
    }
    return list.join(', ');
  }

// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
});
