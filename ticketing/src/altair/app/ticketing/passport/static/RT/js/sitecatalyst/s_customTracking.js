/* PRE-PLUGINS SECTION */
var do_PrePlugins = function() {
// your customized code is here
// Channel Manager Parameter config

	// pageName
	if(!s.pageType&&!s.pageName){
		s.pageName=s.getPageName()
		if(s.pageName)s.pageName=s.pageName.replace(/\.[a-z]+$/,"").replace(":index","")
		if(!s.pageName)s.pageName="top"
	}

	//channel
	if(!s.channel){
		s.channel=s.pageName.split(":")[0]
	}

	//RakutenPageType
	if(s.RakutenPageType && (typeof s.eo == "undefined")){
		s.pageName+="["+s.RakutenPageType+"]"
		s.channel+="["+s.RakutenPageType+"]"
	}
}

/* POST-PLUGINS SECTION */
var do_PostPlugins = function() {
// your customized code is here

	// for MST global tracking
	if(s.events&&s.events.match(/purchase/)){
		//s.events=s.apl(s.events,"event71")
		//s.eVar49=s.prop50+":"+"purchase"
	}
	if(!s.eo&&!s.lnk&&!s.pageType&&!s.un.match(/dev/)&&!s.un.match(/rakutenglobal/)){
		if(s.campaign.match(/_gmx/)||s.campaign.match(/_upc/)||s.eVar49){s.un=s.apl(s.un,"rakutenglobalprod")}
	}
}


/* CUSTOM-PLUGIN SECTION */


/* CODE SECTION - DON'T TOUCH BELOW */
if(s.usePrePlugins)s.doPrePlugins = do_PrePlugins;
if(s.usePostPlugins)s.doPostPlugins = do_PostPlugins;

/************* To Stop Google Preview From Being Counted *************/
if(navigator.userAgent.match(/Google Web Preview/i)){
	s.t=new Function();
	s.tl=new Function();
}
