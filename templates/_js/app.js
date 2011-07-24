

$(document).ready(function() {

    $(".star_off").live('click', function(event) {
        event.preventDefault();
        var href = $(this).attr("href");
        $(this).addClass("star_on");
        $(this).removeClass("star_off");
        $.get(href); 	
    });

    $(".star_on").live('click', function(event) {
        event.preventDefault();
        var href = $(this).attr("href");
        $(this).addClass("star_off");
        $(this).removeClass("star_on");
        $.get(href); 	
    });
    
    $("div.history a").click(function(event) {
        event.preventDefault();
        var href = $(this).attr("href");
        $(this).parent().parent().removeClass("posts");
        $(this).parent().parent().load(href);
	});
		
	$("#loading").bind({
        ajaxStart: function() { $(this).text('Loading...'); },
        ajaxStop: function() { setTimeout($(this).hide(), 2000); }
    });
    
    $(".delete_key a").click(function(event) {
        event.preventDefault();
        var href = $(this).attr("href");
        $.get(href);
        $(this).parent().parent().hide();
    });
	
	
	function confirm_entry(val) {};    
	
});