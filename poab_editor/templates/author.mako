<%inherit file='base.mako' />
<%include file='header.mako' />

<h4>Account Settings</h4>
<hr>
<p>Name: ${ author.name }</p>
<p>Password: ${ author.password }</p>
%if author.group:
  <p>Groups:
  <ul>
  % for group in author.group:
      <li><a href="${ request.route_url('edit_group', name=group.name, action='edit') }">${ group.name }</a></li>
  % endfor
  </ul>
  </p>
%endif

