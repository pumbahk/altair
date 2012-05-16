function get_id(id) {
  return $('input[name=' + id + ']:checked').val() || $('#' + id).val();
}
