jQuery(document).ready(function() {
    //Enter Your Class or ID
    var $stickyMenu = jQuery('.myNav');

    var stickyNavTop = jQuery($stickyMenu).offset().top;

    //Get Height of Navbar Div
    var navHeight = jQuery($stickyMenu).height();

    var stickyNav = function(){
        var scrollTop = jQuery(window).scrollTop();
        if (scrollTop > stickyNavTop) {
            jQuery($stickyMenu).addClass('sticky');
            jQuery('html').css('padding-top', navHeight + 'px')
        } else {
            jQuery($stickyMenu).removeClass('sticky');
            jQuery('html').css('padding-top', '0')
        }
    };

    stickyNav();

    jQuery(window).scroll(function() {
        stickyNav();
    });
});