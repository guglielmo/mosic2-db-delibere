/* Project specific Javascript goes here. */


/* Togglers */
$('.toggle-more').on('click', function(){
    if (this.innerHTML == 'Mostra gli altri valori'){
        this.innerHTML = 'Mostra solo i primi 10 valori'
    } else {
        this.innerHTML = 'Mostra gli altri valori'
    }
 });

$('#toggle-text-preview').on('click', function(){
    if (this.innerHTML == "Mostra l'anteprima del testo della delibera"){
        this.innerHTML = "Nascondi l'anteprima del testo della delibera"
    } else {
        this.innerHTML = "Mostra un'anteprima del testo della delibera"
    }
 });

$('#filtersSidebarButton').on('click', function(){
    div1 = $('.results');
    div2 = $('.sidebar');

    tdiv1 = div1.clone();
    tdiv2 = div2.clone();

    if(!div2.is(':empty')){
        div1.replaceWith(tdiv2);
        div2.replaceWith(tdiv1);
    }

    filters_button = $('#filtersSidebarButton');
    if (filters_button.text() == 'Mostra filtri') {
        filters_button.text('Nascondi filtri');
        $
    } else {
        filters_button.text('Mostra filtri');
    }

});

/* Date pickers */

var date_pickers_options = {
    locale: 'it',
    format: 'DD/MM/YYYY'
};

$('#datetimepicker-start-seduta').datetimepicker(date_pickers_options);
$('#datetimepicker-end-seduta').datetimepicker(date_pickers_options);
$('#datetimepicker-gu').datetimepicker(date_pickers_options);


/* Cookie law JS */
cli_show_cookiebar({
    settings: '{"animate_speed_hide":"500","animate_speed_show":"500","background":"#39414f","border":"#39414f","border_on":true,"button_1_button_colour":"#161616","button_1_button_hover":"#121212","button_1_link_colour":"#ffffff","button_1_as_button":true,"button_2_button_colour":"#000000","button_2_button_hover":"#000000","button_2_link_colour":"#ffffff","button_2_as_button":false,"font_family":"inherit","header_fix":true,"notify_animate_hide":true,"notify_animate_show":false,"notify_div_id":"#cookie-law-info-bar","notify_position_horizontal":"right","notify_position_vertical":"top","scroll_close":false,"scroll_close_reload":false,"showagain_tab":true,"showagain_background":"#fff","showagain_border":"#000","showagain_div_id":"#cookie-law-info-again","showagain_x_position":"5%","text":"#ffffff","show_once_yn":false,"show_once":"10000"}'
});
