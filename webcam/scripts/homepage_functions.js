var adjust_image_width = function(){
    var home_images = getCSSRule('.home_images');
    var w  = window,
    d  = w.document,
    de = d.documentElement,
    db = d.body || d.getElementsByTagName('body')[0],
    x  = w.innerWidth || de.clientWidth || db.clientWidth,
    y  = w.innerHeight|| de.clientHeight|| db.clientHeight;

    if(!!navigator.userAgent.match(/iphone|android|blackberry/ig) && x < 450)
        home_images.style.width = '90%'; 
    else
        home_images.style.width = 'auto';
};

window.onload = adjust_image_width;
window.addEventListener('resize', adjust_image_width);