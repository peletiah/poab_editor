<div>
  %if request.path == '/':
    <a href="/editor">Add a new entry</a>
  %else:
    <a href="/">&#8592; Go to all entries</a>
  %endif
  <span class="admin">
  % if author.id:
    Logged in as: ${ author.name } 
  % else:
    <a href="${ request.route_url('login') }">Login</a>
  % endif
  % if author.name == 'admin':
    &#8226; 
    <a href="/authors">Users</a>
  %endif 
  % if author.id:
    &#8226;
    <a href="${ request.route_url('author', login=author.name) }">Account Settings</a>
    &#8226; 
    <a href="${ request.route_url('logout') }">Logout</a>
  % endif
  </span>
</div>
<hr>
