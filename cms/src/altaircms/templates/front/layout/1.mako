<%inherit file='altaircms:templates/front/ticket-rakuten-co-jp/layout.mako'/>

<div class="section section-main">
    <div id="block_name">
        %if 'block_name' in display_blocks:
            %for widget in display_blocks['block_name']:
               widget id ${widget}
            %endfor
        %endif
    </div>
</div>