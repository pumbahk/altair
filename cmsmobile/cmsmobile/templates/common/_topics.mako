<%page args="topics, topic_renderer" />
<h1>トピックス</h1>
% for topic in topics:
    <li>${topic_renderer.render_cms_link(topic)}</li>
    <li>${topic_renderer.render_genre(topic)}</li>
    <li>${topic_renderer.render_kind(topic)}</li>
% endfor
