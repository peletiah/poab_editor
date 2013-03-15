<%inherit file='base.mako' />

<div>
  <h3>Login</h3>
  <small><a href="/authors">Admin Settings</a></small>
</div>
<hr>


% if failed_attempt:
<p><font color="red">Invalid credentials, try again.</font></p>
% endif
<form class="form-horizontal" method="post" action="${ request.path }">
  <div class="control-group">
    <label class="control-label" for="inputName">Name</label>
    <div class="controls">
      <input type="text" class="input-small" placeholder="Name" name="name" value="${ name }">
    </div>
  </div>
  <div class="control-group">
    <label class="control-label" for="inputPassword">Password</label>
    <div class="controls">
        <input type="password" class="input-small" placeholder="Password" name="password">
    </div>
  </div>
  <input type="hidden" name="next" value="${ next }">
  <div class="control-group">
    <div class="controls">
      <label class="checkbox">
        <input type="checkbox" checked> Remember me
      </label>
      <button type="submit" class="btn" name="submit">Sign in</button>
    </div>
  </div>
</form>

