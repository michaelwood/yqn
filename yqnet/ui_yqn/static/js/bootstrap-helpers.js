/* Copyright: Michael Wood 2019
 * MichaelWood.me.uk
 * Licence: See /LICENCE
 */

$(document).ready(function () {

  $('[data-toggle="popover"]').popover()

  $('[data-toggle="tooltip"]').tooltip()

  /* All the elements that have a title make it
     a nice bootstrap/popover tooltip */
  $("[title]").tooltip({ trigger: "hover"});

  /* Work around a bug that causes tooltips not get dismissed if modal is launched */
  $('.modal').on("show.bs.modal", function(){
    $("[title]").tooltip('hide');
  });

});