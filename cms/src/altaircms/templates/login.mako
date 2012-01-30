<%inherit file='layout.mako'/>
<%block name="content">
    ${message}
    <form action="${url}" method="post">
        <input type="hidden" name="came_from" value="${came_from}"/>
        <input type="text" name="login" value="${login}"/><br/>
        <input type="password" name="password"
               value="${password}"/><br/>
        <input type="submit" name="form.submitted" value="Log In"/>
    </form>

    <form action="/velruse/google/auth" method="post">
        <input type="hidden" name="popup_mode" value="popup">
        <input type="hidden" name="end_point" value="http://communitycookbook.net:6543/login">
        <input type="submit" value="Login with Google">
    </form>
</%block>
