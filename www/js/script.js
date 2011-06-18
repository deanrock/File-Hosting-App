/* rating */
$(document).ready(function() {
        $('.star').bind('click', function() {
            var star = this;
            
            $.get(
            	'/rate/' + $(star).parent().parent().attr('id') + '/' + $(star).attr('title'),
                {'xhr': 'yes'},
                function(r) {
                    $(star).parent().siblings('.current-rating').width(parseInt(r));
                }
            ); 
        });
});

$(document).ready(function() {$("#show_links").fancybox({
				'titlePosition'		: 'inside',
				'transitionIn'		: 'none',
				'transitionOut'		: 'none'
			});
});

function fbs_click() {u=location.href;t=document.title;window.open('http://www.facebook.com/sharer.php?u='+encodeURIComponent(u)+'&t='+encodeURIComponent(t),'sharer','toolbar=0,status=0,width=626,height=436');return false;}