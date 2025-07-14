Drupal.locale = { 'pluralFormula': function ($n) { return Number((($n==1)?(0):((((($n%10)>=2)&&(($n%10)<=4))&&((($n%100)<10)||(($n%100)>=20)))?(1):2))); }, 'strings': {"":{"An AJAX HTTP error occurred.":"Wyst\u0105pi\u0142 b\u0142\u0105d w AJAX HTTP.","HTTP Result Code: !status":"B\u0142\u0105d HTTP: !status","An AJAX HTTP request terminated abnormally.":"Zapytanie AJAX HTTP zosta\u0142o przerwane.","Debugging information follows.":"Informacje diagnostyczne.","Path: !uri":"\u015acie\u017cka: !uri","StatusText: !statusText":"StatusText: !statusText","ResponseText: !responseText":"ResponseText: !responseText","ReadyState: !readyState":"ReadyState: !readyState","Enable":"W\u0142\u0105cz","Disable":"Wy\u0142\u0105cz","Disabled":"Wy\u0142\u0105czone","Enabled":"W\u0142\u0105czone","Edit":"Edytuj","Reset":"Przywr\u00f3\u0107","Add":"Dodaj","Show":"Poka\u017c","Select all rows in this table":"Zaznacza wszystkie wiersze tabeli","Deselect all rows in this table":"Cofa zaznaczenie wszystkich wierszy tabeli","Not published":"Nie do publikacji","Please wait...":"Prosz\u0119 czeka\u0107...","Hide":"Ukryj","Loading":"\u0141adowanie","By @name on @date":"Przez @name w @date","By @name":"Przez @name","Not in menu":"Nie ma w menu","Alias: @alias":"Alias: @alias","No alias":"Brak aliasu","New revision":"Nowa wersja","Drag to re-order":"Chwy\u0107, by zmieni\u0107 kolejno\u015b\u0107","Changes made in this table will not be saved until the form is submitted.":"Zmiany wprowadzone w tabeli zachowuje si\u0119 przyciskiem u do\u0142u formularza.","The changes to these blocks will not be saved until the \u003Cem\u003ESave blocks\u003C\/em\u003E button is clicked.":"Zmiany wprowadzone w blokach zachowuje si\u0119 przyciskiem u do\u0142u formularza.","This permission is inherited from the authenticated user role.":"Te uprawnienia s\u0105 dziedziczone wed\u0142ug roli zalogowanego u\u017cytkownika.","No revision":"Brak wersji","@number comments per page":"@number komentarzy na stronie","Requires a title":"Tytu\u0142 wymagany","Not restricted":"Bez ogranicze\u0144","(active tab)":"(aktywna karta)","Not customizable":"Niekonfigurowalne","Restricted to certain pages":"Ograniczenie do okre\u015blonych stron.","The block cannot be placed in this region.":"Blok nie mo\u017ce by\u0107 umieszczony w tym obszarze.","Hide summary":"Ukryj podsumowanie","Edit summary":"Edycja podsumowania","Don\u0027t display post information":"Ukrycie informacji o wpisie","@title dialog":"@title dialog","The selected file %filename cannot be uploaded. Only files with the following extensions are allowed: %extensions.":"Wybrany plik %filename nie m\u00f3g\u0142 zosta\u0107 wys\u0142any. Dozwolone s\u0105 jedynie nast\u0119puj\u0105ce rozszerzenia: %extensions.","Re-order rows by numerical weight instead of dragging.":"Zmie\u0144 kolejno\u015b\u0107 wierszy podaj\u0105c warto\u015bci numeryczne zamiast przeci\u0105gaj\u0105c.","Show row weights":"Poka\u017c wagi wierszy","Hide row weights":"Ukryj wagi wierszy","Autocomplete popup":"Okienko autouzupe\u0142niania","Searching for matches...":"Wyszukiwanie pasuj\u0105cych...","Remove group":"Usu\u0144 grup\u0119","Apply (all displays)":"Zastosuj (wszystkie formaty)","Revert to default":"Przywr\u00f3\u0107 domy\u015blne","Apply (this display)":"Zastosuj (ten format)","Hide description":"Ukryj opis","Show description":"Wy\u015bwietl opis","Breadcrumbs":"Breadcrumby","Show layout designer":"Poka\u017c projektowanie uk\u0142adu","Hide layout designer":"Ukryj kreatora uk\u0142adu","Remove this pane?":"Usun\u0105\u0107 to okienko?","Now Editing: ":"Teraz edytowane: ","Loading token browser...":"\u0141adowanie przegl\u0105darki wzorc\u00f3w...","Available tokens":"Dost\u0119pne \u017cetony","Insert this token into your form":"Wstaw ten wzorzec do formularza","First click a text field to insert your tokens into.":"Najpierw kliknij w pole tekstowe, do kt\u00f3rego b\u0119d\u0105 wstawione wzorce.","Automatic alias":"Alias automatyczny","Zoom level":"Poziom przybli\u017cenia","Select all":"Zaznacz wszystko","Deselect all":"Odznacz wszystko","Saving vote...":"Zapisywanie g\u0142osu...","Close":"Zamknij","Received an invalid response from the server.":"Otrzymano nieprawid\u0142owy komunikat z serwera.","Select all children":"Wybierz wszystkie podrz\u0119dne","Translate Text":"Przet\u0142umacz tekst","An HTTP error @status occured.":"Wyst\u0105pi\u0142 b\u0142\u0105d HTTP: @status","Inclusion: @value":"Do\u0142\u0105czenie: @value","Priority: @value":"Priorytet: @value","One domain with multiple subdomains":"Jedna domena z wieloma subdomenami","Universal web tracking opt-out":"Uniwersalne odst\u0105pienie od \u015bledzenia w sieci","A single domain":"Pojedyncza domena","All pages with exceptions":"Wszystkie strony z wyj\u0105tkami","Excepted: @roles":"Wykluczone: @roles","On by default with opt out":"Domy\u015blnie w\u0142\u0105czone z mo\u017cliwo\u015bci\u0105 odst\u0105pienia","Off by default with opt in":"Domy\u015blnie wy\u0142\u0105czone z mo\u017cliwo\u015bci\u0105 przyst\u0105pienia","Downloads":"Pobrania","Not tracked":"Nie \u015bledzone","@items enabled":"@items aktywne","Site search":"Wyszukiwanie strony","No privacy":"Brak prywatno\u015bci","Colorbox":"Colorbox"}} };;
/**
* @file
* Javascript, modifications of DOM.
*
* Manipulates links to include jquery load funciton
*/

(function ($) {
  Drupal.behaviors.jquery_ajax_load = {
    attach: function (context, settings) {
      jQuery.ajaxSetup ({
      // Disable caching of AJAX responses
        cache: false
      });

      var trigger = Drupal.settings.jquery_ajax_load.trigger;
      var target = Drupal.settings.jquery_ajax_load.target;
      // Puede ser más de un valor, hay que usar foreach()
      $(trigger).once(function() {
        var html_string = $(this).attr( 'href' );
        // Hay que validar si la ruta trae la URL del sitio
        $(this).attr( 'href' , target );
        var data_target = $(this).attr( 'data-target' );
        if (typeof data_target === 'undefined' ) {
          data_target = target;
        }
        else {
          data_target = '#' + data_target;
        }
        $(this).click(function(evt) {
          evt.preventDefault();
          jquery_ajax_load_load($(this), data_target, html_string);
        });
      });
      $(trigger).removeClass(trigger);
    }
  };  

// Handles link calls
  function jquery_ajax_load_load(el, target, url) {
    var module_path = Drupal.settings.jquery_ajax_load.module_path;
    var toggle = Drupal.settings.jquery_ajax_load.toggle;
    var base_path = Drupal.settings.jquery_ajax_load.base_path;
    var animation = Drupal.settings.jquery_ajax_load.animation;
    if( toggle && $(el).hasClass( "jquery_ajax_load_open" ) ) {
      $(el).removeClass( "jquery_ajax_load_open" );
      if ( animation ) {
        $(target).hide('slow', function() {
          $(target).empty();
        });
      }
      else {
        $(target).empty();
      }
    }
    else {
      var loading_html = Drupal.t('Loading'); 
      loading_html += '... <img src="/';
      loading_html += module_path;
      loading_html += '/jquery_ajax_load_loading.gif">';
      $(target).html(loading_html);
      $(target).load(base_path + 'jquery_ajax_load/get' + url, function( response, status, xhr ) {
        if ( status == "error" ) {
          var msg = "Sorry but there was an error: ";
          $(target).html( msg + xhr.status + " " + xhr.statusText );
        }
        else {
          if ( animation ) {
            $(target).hide();
            $(target).show('slow')
          }
//        Drupal.attachBehaviors(target);
        }
      });
      $(el).addClass( "jquery_ajax_load_open" );
    }
  }
}(jQuery));
;
(function($) {
  Drupal.behaviors.custom_search = {
    attach: function(context) {

      if (!Drupal.settings.custom_search.solr) {
        // Check if the search box is not empty on submit
        $('form.search-form', context).submit(function(){
          var $this = $(this);
          var box = $this.find('input.custom-search-box');
          if (box.val() != undefined && box.val() == '') {
            $this.find('input.custom-search-box').addClass('error');
            return false;
          }
          // If basic search is hidden, copy or value to the keys
          if ($this.find('#edit-keys').parents('div.element-invisible').attr('class') == 'element-invisible') {
            $this.find('#edit-keys').val($this.find('#edit-or').val());
            $this.find('#edit-or').val('');
          }
          return true;
        });
      }

      // Search from target
      $('form.search-form').attr('target', Drupal.settings.custom_search.form_target);

      // Displays Popup.
      $('form.search-form input.custom-search-box', context).bind('click focus', function(e){
        var $parentForm = $(this).parents('form');
        // check if there's something in the popup and displays it
        var popup = $parentForm.find('fieldset.custom_search-popup');
        if (popup.find('input,select').length && !popup.hasClass('opened')) {
          popup.fadeIn().addClass('opened');
        }
        e.stopPropagation();
      });
      $(document).bind('click focus', function(){
        $('fieldset.custom_search-popup').hide().removeClass('opened');
      });

      // Handle checkboxes
      $('.custom-search-selector input:checkbox', context).each(function(){
        var el = $(this);
        if (el.val() == 'c-all') {
          el.change(function(){
            $(this).parents('.custom-search-selector').find('input:checkbox[value!=c-all]').attr('checked', false);
          });
        }
        else {
          if (el.val().substr(0,2) == 'c-') {
            el.change(function(){
              $('.custom-search-selector input:checkbox').each(function(){
                if ($(this).val().substr(0,2) == 'o-') {
                  $(this).attr('checked', false);
                }
              });
              $(this).parents('.custom-search-selector').find('input:checkbox[value=c-all]').attr('checked', false);
            });
          } else {
            el.change(function(){
              $(this).parents('.custom-search-selector').find('input:checkbox[value!=' + el.val() + ']').attr('checked', false);
            });
          }
        }
      });

      // Handle popup.
      var popup = $('fieldset.custom_search-popup:not(.custom_search-processed)', context).addClass("custom_search-processed");
      popup.click(function(e){
        e.stopPropagation();
      })
      popup.append('<a class="custom_search-popup-close" href="#">' + Drupal.t('Close') + '</a>');
      $('a.custom_search-popup-close').click(function(e){
        $('fieldset.custom_search-popup.opened').hide().removeClass('opened');
        e.preventDefault();
      });

    }
  }
})(jQuery);
;
(function ($) {

$(document).ready(function() {

  // Attach mousedown, keyup, touchstart events to document only and catch
  // clicks on all elements.
  $(document.body).bind("mousedown keyup touchstart", function(event) {

    // Catch the closest surrounding link of a clicked element.
    $(event.target).closest("a,area").each(function() {

      if (Drupal.settings.matomo.trackMailto && $(this).is("a[href^='mailto:'],area[href^='mailto:']")) {
        // Mailto link clicked.
        _paq.push(["trackEvent", "Mails", "Click", this.href.substring(7)]);
      }

    });
  });

  // Colorbox: This event triggers when the transition has completed and the
  // newly loaded content has been revealed.
  if (Drupal.settings.matomo.trackColorbox) {
    $(document).bind("cbox_complete", function () {
      var href = $.colorbox.element().attr("href");
      if (href) {
        _paq.push(["setCustomUrl", href]);
        _paq.push(["trackPageView"]);
      }
    });
  }

});

})(jQuery);
;
