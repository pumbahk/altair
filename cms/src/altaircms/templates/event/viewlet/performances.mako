<%namespace name="gadgets" file="../../gadgets.mako"/>

<div class="box">
  <p align="right">※ pc購入URL,mobile購入URLは、個別に飛び先のURLが設定されている場合にy。そうでない場合にはnが付きます。</p>
  <table class="table">
    <thead>
	  <tr>    
		<th></th>
		<th>公演名</th>
		<th>バックエンドID</th>
		<th>公演日時</th>
		<th>場所</th>
		<th>pc購入URL</th>
		<th>mobile購入URL</th>
	  </tr>       
    </thead>
    <tbody>
         %for p in performances:
           <tr>
             <td>
               <input type="radio" name="object_id" value="${p.id}">
             </td>
             <td><a href="${request.route_path("performance_update",action="detail",id=p.id)}">${p.title }</a></td>
             <td>${p.backend_id}</td><td>${ p.start_on }</td><td>${ p.venue }</td>
             <td>${u'<a href="%s">y</a>' % p.purchase_link if p.purchase_link else "n"|n}</td>
             <td>${u'<a href="%s">y</a>' % p.mobile_purchase_link if p.mobile_purchase_link else "n"|n}</td>
           </tr>
         %endfor
    </tbody>
  </table>

  ${gadgets.getti_update_code(performances,"getti_submit")}

  ## button group
  <div class="btn-group">
    <a href="${request.route_path("performance_update",action="input",id="__id__")}" class="btn action">
      <i class="icon-pencil"></i> 編集
    </a>
    <button class="btn dropdown-toggle" data-toggle="dropdown">
        <span class="caret"></span>
    </button>
    <ul class="dropdown-menu">
      <li>
        <a href="${request.route_path("performance_update",action="detail",id="__id__")}" class="action">
          <i class="icon-pencil"></i> 詳細画面
        </a>
      </li>
      <li>
        <a href="${request.route_path("performance_update",action="input",id="__id__")}" class="action">
          <i class="icon-minus"></i> 編集
        </a>
      </li>
      <li>
        <a href="${request.route_path("performance_create", action="copied_input",_query=dict(id="__id__"))}" class="action">
          <i class="icon-minus"></i> コピーして新規作成
        </a>
      </li>
      <li>
        <a href="${request.route_path("performance_create",action="input",_query=dict(event=event.id))}">
          <i class="icon-minus"></i> 新規作成
        </a>
      </li>
      <li>
        <a href="${request.route_path("performance_delete", action="confirm", id="__id__")}" class="action">
          <i class="icon-minus"></i> 削除
        </a>
      </li>
      <li class="divider"></li>
      <li>${ gadgets.getti_update_code_button()}</li>
    </ul>
  </div>
</div>

