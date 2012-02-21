% for image in image_assets:
   ## <img pk="${image.id}" src="${image.filepath}" />
      <img pk="${image.id}" src="${request.route_url('asset_edit', asset_id=image.id)}?raw=t" alt=""/>
% endfor 
