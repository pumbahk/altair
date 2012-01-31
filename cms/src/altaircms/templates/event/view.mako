<%inherit file='../layout.mako'/>

<h1>${event.title}</h1>
<a href="">preview</a> <a href="">sync</a>

<hr/>

<a href="/page/edit">add page</a>
<h2>page list</h2>


<table>
    <tbody>
    <tr>
        <th>ID</th><td>${event.id}</td>
    </tr>
    </tbody>
</table>
