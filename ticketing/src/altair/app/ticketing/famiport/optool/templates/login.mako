<!DOCTYPE html>
<html>

<%include file="header.mako"/>

  <body>
    <div class="container">
      <form class="form-signin">
        <h2 class="form-signin-heading">プレイガイド様名</h2>
        <div class="form-group">
          <label>利用者ID
          <input type="text" name="login_id" class="form-control" placeholder="ID" required autofocus></label>
          <label>パスワード
          <input type="password" name="password" class="form-control" placeholder="Password" required></label>
        </div>
        <a href="search.html">
          <button type="submit" class="btn btn-lg btn-primary btn-block">Sign in</button>
        </a>
      </form>
      <footer style="text-align:center;">
        <div>&copy; 2012 TicketStar Inc.</div>
        <div>version =</div>
      </footer>
    </div>
  </body>
</html>
