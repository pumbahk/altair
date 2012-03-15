<style>
#navigation { height:25px; }
#navigation ul{ list-style-type: none; padding-top:17px; font-size:11px; }
#navigation ul li{ float:left; display:inline; margin-right:5px;}
#navigation ul li a,
#navigation ul li a span { float:left; display:inline; height:25px; padding:0 0 0 8px; background:url(/static/img/nav.gif) no-repeat 0 0; }
#navigation ul li a span { padding:0 8px 0 0; background-position:right 0; }
#navigation ul li a { color:#ddadab; line-height:29px;}
#navigation ul li a.active { font-weight: bold;}

#navigation ul li a:hover,
#navigation ul li a.active { background-position:0 bottom; color:#887e42; }

#navigation ul li a:hover span,
#navigation ul li a.active span{ background-position:right bottom; }
</style>
<div class="navbar navbar-fixed-top">
    <div class="navbar-inner">
        <div class="container">
            <a class="brand" href="/"><img src="/static/img/altair_logo.png"></a>
            <div class="nav-collapse">
                <ul class="nav pull-right">
                        % if user:
                            <li class="dropdown">
                                <a href="#" class="dropdown-toggle" data-toggle="dropdown">${user.screen_name}<b class="caret"></b></a>
                                <ul class="dropdown-menu">
                                    <li><a href="#">
                                        <i class="icon-cog"> </i>
                                        Settings</a>
                                    </li>
                                    <li><a href="${request.route_path("logout")}">
                                        <i class="icon-off"> </i>
                                        Logout</a>
                                    </li>
                                </ul>
                            </li>
                        % else:
                            <li><a href="${request.route_path("oauth_entry")}">Login with Twitter (OAuth)</a></li>
                        % endif
                </ul>
            </div><!--/.nav-collapse -->
                <!-- Navigation -->
                <div id="navigation">
                    <ul>
                        <li><a href=""><span>ダッシュボード</span></a></li>
                        <li><a href="http://localhost:7654/"><span>票券管理</span></a></li>
                        <li><a href="http://127.0.0.1:6543/" class="active"><span>CMS</span></a></li>
                    </ul>
                </div>
                <!-- End Navigation -->
        </div>
    </div>
</div>
