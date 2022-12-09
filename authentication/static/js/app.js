$(document).ready(function () {
  $(document).on("click", ".lmd-square-payment", function () {
      $(".lmd-square-payment1").removeClass("lmd-radio-clicked");
      $(this).toggleClass("lmd-radio-clicked");
      $('.payment_shipping_address').hide();
  });

  $(document).on("click", ".lmd-square-payment1", function () {
    $(".lmd-square-payment").removeClass("lmd-radio-clicked");
    $(this).toggleClass("lmd-radio-clicked");
    $('.payment_shipping_address').show();
    $('.payment_shipping_row').show();
});

  $(document).on("click", ".lmd-square", function () {
    $(".lmd-square1").removeClass("lmd-radio-clicked");
    $(this).toggleClass("lmd-radio-clicked");
  });

  $(document).on("click", ".lmd-square1", function () {
    $(".lmd-square").removeClass("lmd-radio-clicked");
    $(this).toggleClass("lmd-radio-clicked");
  });
  

  $('#credit-card').on('keypress change blur', function () {
    $(this).val(function (index, value) {
        return value.replace(/[^a-z0-9]+/gi, '').replace(/(.{4})/g, '$1 ');
    });
});

$('#credit-card').on('copy cut paste', function () {
    setTimeout(function () {
        $('#credit-card').trigger("change");
    });
});


function GetCardType(number)
{
    // visa
    var re = new RegExp("^4");
    if (number.match(re) != null)
        return "Visa";

    // Mastercard 
    // Updated for Mastercard 2017 BINs expansion
     if (/^(5[1-5][0-9]{14}|2(22[1-9][0-9]{12}|2[3-9][0-9]{13}|[3-6][0-9]{14}|7[0-1][0-9]{13}|720[0-9]{12}))$/.test(number)) 
        return "Mastercard";

    // AMEX
    re = new RegExp("^3[47]");
    if (number.match(re) != null)
        return "AMEX";

    // Discover
    re = new RegExp("^(6011|622(12[6-9]|1[3-9][0-9]|[2-8][0-9]{2}|9[0-1][0-9]|92[0-5]|64[4-9])|65)");
    if (number.match(re) != null)
        return "Discover";

    // Diners
    re = new RegExp("^36");
    if (number.match(re) != null)
        return "Diners";

    // Diners - Carte Blanche
    re = new RegExp("^30[0-5]");
    if (number.match(re) != null)
        return "Diners - Carte Blanche";

    // JCB
    re = new RegExp("^35(2[89]|[3-8][0-9])");
    if (number.match(re) != null)
        return "JCB";

    // Visa Electron
    re = new RegExp("^(4026|417500|4508|4844|491(3|7))");
    if (number.match(re) != null)
        return "Visa Electron";

    return "";
}

});

