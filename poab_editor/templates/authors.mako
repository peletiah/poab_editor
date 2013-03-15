<%inherit file='base.mako' />
<%include file='header.mako' />

<h4>Authors</h4>
<hr>
% for name in authors:
<p><a href="${ request.route_url('author', login=name) }">${ name }</a></p>
% endfor
