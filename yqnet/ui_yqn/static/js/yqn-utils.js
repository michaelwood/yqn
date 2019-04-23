"use strict";

/* Copyright: Michael Wood 2019
 * MichaelWood.me.uk
 * Licence: See /LICENCE
 */

var COOKIE_NAME = "yqn-site-settings";
var COOKIE_SETTINGS = { path: "/" };

var yqnUtils = {
    /* From libtoaster Michael Wood GPLv2 */
    urlParams: function (obj){
        var str = "?";

        for (var key in obj){
          if (obj[key] === undefined)
            continue;

          str += key+ "="+obj[key].toString();
          str += "&";
        }

        /* Maintain the current hash */
        str += window.location.hash;

        return str;
      },

      setCookieData: function (data) {
        Cookies.set(COOKIE_NAME, data, COOKIE_SETTINGS);
      },
      getCookieData: function () {
        return Cookies.getJSON(COOKIE_NAME);
      },

      delete: function (url, successCb){
         $.ajax({
           type: "DELETE",
           url: url,
           contentType: "application/json",
           accept: "application/json",
           headers: { "X-CSRFToken": Cookies.get("csrftoken") },
           success: function() {
             console.log("deleted");
             if (successCb){
              successCb();
             }
           },
           error: function(error) {
             console.log(error.responseText);
           }
         });
      },

      /* great idea from https://stackoverflow.com/questions/315760/what-is-the-best-way-to-determine-the-number-of-days-in-a-month-with-javascript#315767 */
      getDaysInMonth: function(calenderMonth){
        let now = new Date();
        return new Date(now.getFullYear(), calenderMonth, 0).getDate();
      },

      share: function(url){

        /* If we've been passed a relative url then fully qualify it */
        if (url.indexOf("://") === -1){
          url = window.location.origin + url;
        }

        let text  = encodeURIComponent("This is interesting " +url+ " (via Quakr)");

        $("#share-twitter").prop("href", "https://twitter.com/home?status="+text);
        $("#share-facebook").prop("href", "https://www.facebook.com/sharer/sharer.php?u="+encodeURIComponent(url));
        $("#share-email").prop("href", "mailto:?subject=You%20might%20be%20interested%20in%20this%20(via%20Quakr)&body="+text);

        $("#url-input").prop("value", url);

        $("#share-link").click(function(e){
          e.preventDefault();
          let urlInput = $("#url-input");

          urlInput.toggleClass("d-none");

          urlInput.focus();
          urlInput.select();

          /* Doesn't work in universally yet but is not crucial */
          try {
            let success = document.execCommand('copy');
            if (success){
              yqnBus.$emit("notify", {"title": "Copied", "body": "Url copied to clipboard" });
            }
          } catch (err) {
            console.log("Copy not supported");
          }
        });

        $("#share-modal").modal("show");
      },
};

var yqnBus = new Vue();

/* Make sure the csrftoken is sent on ajax requests
 * From Django Docs
 */

function csrfSafeMethod(method) {
  // these HTTP methods do not require CSRF protection
  return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$.ajaxSetup({
  beforeSend: function(xhr, settings) {
      if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
          xhr.setRequestHeader("X-CSRFToken", Cookies.get("csrftoken"));
      }
  }
});

function setActivePage(){
 $(".nav-scroller .nav-link").each(function(){
   if($(this).prop("href") == window.location.href){
     $(this).addClass("bg-dark");
   } else {
     $(this).removeClass("bg-dark");
   }

 });


}

$(document).ajaxStart(function(){
  $("#ajax-loading-spinner").show();
});

$(document).ajaxComplete(function(){
  $("#ajax-loading-spinner").hide();
});


$(document).ready(function(){

  var settingsCookie = yqnUtils.getCookieData()

  if (!settingsCookie){
    $("#yqn-welcome-msg").show();
  }

  yqnUtils.setCookieData({ last_time: Date.now() });

  $("[data-toggle='add-object-modal']").click(function(){
    yqnBus.$emit("modal", $(this).data("options"));
  });

  setActivePage();

  maybePulseMenuBtn();

});

function maybePulseMenuBtn(){

  if ($(window).width() < 991.98){
    console.log("maybe pulse menu bnt");
    $(".navbar-toggler").addClass("pulse-navbar-toggler");
    /* Disconnect we only need to do this once */
    window.onresize = null;
  }
}

window.onresize = maybePulseMenuBtn;


/* prevent Bootstrap from hijacking TinyMCE modal focus
 Its all getting a bit too modal out there...
*/

$(document).on('focusin', function(e) {
  if ($(e.target).closest(".mce-window").length) {
    e.stopImmediatePropagation();
  }
});