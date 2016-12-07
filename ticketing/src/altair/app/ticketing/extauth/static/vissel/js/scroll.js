var syncerTimeout = null ;
$( function(){
	$( window ).scroll( function()
	{
		if( syncerTimeout == null )
		{
			syncerTimeout = setTimeout( function(){
				var element = $( '#topButton' ) ;
				var visible = element.is( ':visible' ) ;
				var now = $( window ).scrollTop() ;
				var under = $( 'body' ).height() - ( now + $(window).height() ) ;
				if( now > 400 && 200 < under )
				{
					if( !visible )
					{
						element.fadeIn( 'slow' ) ;
					}
				}
				else if( visible )
				{
					element.fadeOut( 'slow' ) ;
				}
				syncerTimeout = null ;
			} , 1000 ) ;
		}
	} ) ;
	$( '#topButton a' ).click(
		function()
		{
			$( 'html,body' ).animate( {scrollTop:0} , 'slow' ) ;
		}
	) ;
} ) ;