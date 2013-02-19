<h1>ピックアップ</h1>
    % if promotions:
        % for promo in promotions:
            <a href="${promo.link}">${promo.text}</a>
        % endfor
    % endif
<p/>