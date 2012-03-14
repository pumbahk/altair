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
        </div>
    </div>
</div>
