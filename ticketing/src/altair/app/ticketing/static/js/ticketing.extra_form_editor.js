(function (fn) {
  define(['altair.dynpredicate'], fn);
})(function (dynpredicate) {
  var translations = {
    'ja': {
      'kind': {
        'text': '自由入力',
        'password': 'パスワード',
        'textarea': '自由入力ボックス',
        'select': 'プルダウン',
        'multiple_select': 'リストボックス (複数選択可)',
        'radio': 'ラジオボタン',
        'checkbox': 'チェックボックス',
        'date': '日付',
        'description_only': '説明文のみ'
      },
      'placeholder': {
        'name': 'フィールド名',
        'display_name': '表示名',
        'description': '説明文 (上)',
        'note': '説明文 (下)',
        'conditional_expressions': '条件式'
      },
      'action': {
        'add_new_value': '値を追加'
      },
      'message': {
        'label_already_exists': 'ラベル{}はすでに存在します',
        'must_be_equal_to_or_greater_than': '{}以上の数値を指定してください',
        'must_be_equal_to_or_less_than': '{}以下の数値を指定してください',
        'must_be_less_than': '{}未満の数値を指定してください',
        'must_be_a_number': '数値を指定してください',
        'must_choose_at_least_one_validator_type': '少なくとも一つ選択してください'
      },
      'label': 'ラベル',
      'value': '値',
      'required': '必須',
      'show_on_entry': '購入画面に表示',
      'show_in_orderreview': '予約確認画面に表示',
      'edit_in_orderreview': '予約確認画面で編集',
      'max_length': '最大入力文字数',
      'remove': '削除',
      'validators': '入力値の制限',
      'activation_conditions': '有効化条件',
      'validator': {
        'numerics': '数字',
        'alphabets': 'アルファベット',
        'hiragana': 'ひらがな',
        'katakana': 'カタカナ',
        'other_characters': 'その他の文字'
      },
    }
  };

  var config = {
    'make_name_idential_to_display_name': true
  };

  function parseIntExactly(x) {
    var r = x * 1;
    return isNaN(r) ? r: r|0;
  }

  function configuration_form_content_view_text(model) {
    return new TextConfigurationView({ model: model });
  }

  function configuration_form_content_view_select(model) {
    var $a = $('<a href="#" class="action-add_new_value"></a>').text(translations['ja']['action']['add_new_value']);
    var $tbody = $('<tbody></tbody>')
      .append($('<tr class="last"></tr>').append($('<td colspan="3"></td>').append($a)));
    var $table = $(
      '<table class="table table-condensed">' +
      '<thead>' +
      '<tr>' +
      '<th>ラベル</th>' +
      '<th>値</th>' +
      '<th></th>' +
      '</tr>' +
      '</thead>' +
      '</table>');
    $table.append($tbody);
    var retval = new SelectConfigurationView({ model: model, el: $table[0] });
    $a.on('click', function () { retval.trigger('new'); return false; });
    return retval;
  }

  var TextFieldPreviewView = Backbone.View.extend({
    tagName: 'div',

    initialize: function () {
      this.model.on('change:type', this.render, this);
      this.model.on('change:max_length', function () {
        this.$el.find('input').attr("maxlength", this.model.get('max_length'));
      }, this);
    },

    render: function () {
      this.$el
        .empty()
        .append(
          $('<input type="text" class="input-medium" />')
          .attr("maxlength", this.model.get('max_length'))
        );
      return this;
    }
  });

  var PasswordFieldPreviewView = Backbone.View.extend({
    tagName: 'div',

    initialize: function () {
      this.model.on('change:type', this.render, this);
      this.model.on('change:max_length', function () {
        this.$el.find('input').attr("maxlength", this.model.get('max_length'));
      }, this);
    },

    render: function () {
      this.$el
        .empty()
        .append(
          $('<input type="password" class="input-medium" />')
          .attr("maxlength", this.model.get('max_length'))
        );
      return this;
    }
  });

  var TextBoxPreviewView = Backbone.View.extend({
    tagName: 'div',

    initialize: function () {
      this.model.on('change:type', this.render, this);
      this.model.on('change:max_length', function () {
        this.$el.find('textarea').attr("maxlength", this.model.get('max_length'));
      }, this);
    },

    render: function () {
      this.$el
        .empty()
        .append(
          $('<textarea></textarea>')
          .attr("maxlength", this.model.get('max_length'))
        );
      return this;
    }
  });

  var SelectBoxPreviewView = Backbone.View.extend({
    tagName: 'div',

    initialize: function () {
      this.model.on('change', this.render, this);
      this.model.get('choices').on('add remove', this.render, this);
    },

    render: function () {
      var $select = $('<select class="input-medium"></select>');
      this.model.get('choices').each(function (choice) {
        $select.append(
          $('<option></option>')
            .attr('value', choice.get('value'))
            .text(choice.get('label'))
        );
      });
      if (this.options.multiple)
        $select.attr("multiple", "multiple");
      this.$el.empty().append($select);
    },
  });

  var CheckboxPreviewView = Backbone.View.extend({
    tagName: 'div',

    initialize: function () {
      this.model.on('change', this.render, this);
      this.model.get('choices').on('change add remove', this.render, this);
    },

    render: function () {
      var type = this.options.type;
      this.$el.addClass('input-group').empty();
      var self = this;
      this.model.get('choices').each(function (choice) {
        self.$el.append(
          $('<label></label>')
          .addClass(type)
          .text(choice.get('label'))
          .prepend(
            $('<input></input>')
            .attr('name', 'field-' + self.model.cid)
            .attr('type', type)
            .attr('value', choice.get('value')) 
          )
        );
      });
    }
  });

  var renderJapaneseDateFields = function ($el, year, month, day) {
    var date = new Date();
    var $year = $('<select style="width:6em"></select>');
    for (var i = Math.max(0, date.getYear() - 50) + 1900, e = date.getYear() + 50 + 1900; i < e; i++) {
      var option = $('<option></option>').text(i +  "");
      if (i == year)
        option.attr('selected', 'selected');
      $year.append(option);
    }
    var $month = $('<select style="width:4em"></select>');
    for (var i = 1; i <= 12; i++) {
      var option = $('<option></option>').text(i + "");
      if (i == month)
        option.attr('selected', 'selected');
      $month.append(option);
    }
    var $day = $('<select style="width:4em"></select>');
    for (var i = 1; i <= 31; i++) {
      var option =$('<option></option>').text(i + "");
      if (i == day)
        option.attr('selected', 'selected');
      $day.append(option);
    }
    return $el
      .append($year)
      .append(document.createTextNode('年'))
      .append($month)
      .append(document.createTextNode('月'))
      .append($day)
      .append(document.createTextNode('日'));
  };

  var dateFieldRenderers = {
    'ja': renderJapaneseDateFields
  };

  var DateFieldPreviewView = Backbone.View.extend({
    tagName: 'div',
    dateFieldRenderers: dateFieldRenderers,

    initialize: function () {
      this.model.on('change:type', this.render, this);
    },

    render: function () {
      var date = new Date();
      var year = date.getYear() + 1900, month = date.getMonth() + 1, day = date.getDate();
      this.dateFieldRenderers['ja'](this.$el.css('white-space', 'nowrap').empty(), year, month, day);
      return this.$el;
    }
  });

  var DescriptionOnlyRowConfigurationView = Backbone.View.extend({
    initialize: function (options) {
      this.$outer = options ? options.outer: null;
    },

    render: function () {
      this.$outer.find('textarea[name="note"], input[name="required"], input[name="display_name"], input[name="activation_conditions"]').attr('disabled', 'disabled');
      return this;
    },

    remove: function () {
      this.$outer.find('textarea[name="note"], input[name="required"], input[name="display_name"], input[name="activation_conditions"]').attr('disabled', null);
      Backbone.View.prototype.remove.apply(this, arguments);
    }
  });

  var handler_factories = {
    'text': function () {
      return {
        preview_view: function (model) {
          return new TextFieldPreviewView({ model: model });
        },
        configuration_form_content_view: configuration_form_content_view_text
      };
    },
    'password': function () {
      return {
        preview_view: function (model) {
          return new PasswordFieldPreviewView({ model: model });
        },
        configuration_form_content_view: configuration_form_content_view_text
      };
    },
    'textarea': function () {
      return {
        preview_view: function (model) {
          return new TextBoxPreviewView({ model: model });
        },
        configuration_form_content_view: configuration_form_content_view_text
      };
    },
    'select': function () {
      return {
        preview_view: function (model) {
          return new SelectBoxPreviewView({ model: model, multiple: false });
        },
        configuration_form_content_view: configuration_form_content_view_select
      };
    },
    'multiple_select': function () {
      return {
        preview_view: function (model) {
          return new SelectBoxPreviewView({ model: model, multiple: true });
        },
        configuration_form_content_view: configuration_form_content_view_select
      };
    },
    'radio': function () {
      return {
        preview_view: function (model) {
          return new CheckboxPreviewView({ model: model, type: 'radio' });
        },
        configuration_form_content_view: configuration_form_content_view_select
      };
    },
    'checkbox': function () {
      return {
        preview_view: function (model) {
          return new CheckboxPreviewView({ model: model, type: 'checkbox' });
        },
        configuration_form_content_view: configuration_form_content_view_select
      };
    },
    'date': function () {
      return {
        preview_view: function (model) {
          return new DateFieldPreviewView({ model: model });
        },
        configuration_form_content_view: function (model, $el) {
          return new DateConfigurationView({ model: model, el: $('<div></div>') });
        }
      };
    },
    'description_only': function () {
      return {
        preview_view: function (model) {
          // an empty view
          return new Backbone.View({ model: model });
        },
        configuration_form_content_view: function (model, $el) {
          return new DescriptionOnlyRowConfigurationView({ model: model, outer: $el });
        }
      };
    }
  };

  var Choice = Backbone.Model.extend({
    defaults: {
      value: '',
      label: ''
    }
  });

  var Choices = Backbone.Collection.extend({
    model: Choice,
    map_view: null,

    initialize: function () {
      this.map_view = {};

      var self = this;
      this.on('add', function (model) {
        model.on('change', function (model) {
          var label = model.get('label');
          var existing_model = self.map_view[label];
          if (existing_model !== void(0) && existing_model !== model) {
            model.trigger('validated', model, translations['ja']['message']['label_already_exists'])
            return;
          } else {
            model.trigger('validated', model, null);
          }
          self.map_view[label] = model;
        }, this);
      }, this);

      this.on('remove', function (model) {
        model.off('change', null, this);
      }, this);
    },

    reset: function () {
      Backbone.Collection.prototype.reset.apply(this, arguments);
      var self = this;
      this.map_view = {};
      _.each(this.models, function (model) {
        var label = model.get('label');
        self.map_view[label] = model;
      });
    },

    validate: function () {
      var choices = {};
      this.each(function (choice) {
        var label = choice.get('label')
        if (choices[label] !== void(0))
          return translations['ja']['message']['label_already_exists'].replace('{}', label);
        choices[label] = true;
      });
      return null;
    }
  });

  var ChoiceView = Backbone.View.extend({
    tagName: 'tr',

    initialize: function () {
      var self = this;
      this.model.on('validated', function (model, error) {
        if (error)
          self.$el.addClass('error');
        else
          self.$el.removeClass('error');
      });
    },

    render_value: function () {
      var retval = $('<input type="text" class="input-small" />')
        .val(this.model.get('value'));
      var self = this;
      retval.on('change', function (e) { self.model.set('value', this.value); });
      return retval;
    },

    render_label: function () {
      var retval = $('<input type="text" class="input-small" />')
        .val(this.model.get('label'))
      var self = this;
      retval.on('change', function (e) { self.model.set('label', this.value); });
      return retval;
    },

    render: function () {
      var self = this;
      var $btn_remove = $('<a href="#"><i class="icon-remove"></i></a>');
      $btn_remove.on('click', function () {
        self.trigger('remove');
      });
      this.$el
        .empty()
        .addClass('control-group')
        .append($('<td></td>').append(this.render_label()))
        .append($('<td></td>').append(this.render_value()))
        .append($('<td></td>').append($btn_remove));
      return this;
    }
  });

  var DefaultValidatorSetting = Backbone.Model.extend({
    defaults: {
      enabled: null
    }
  });

  var validatorDefs = [
    { name: 'numerics', model: DefaultValidatorSetting },
    { name: 'alphabets', model: DefaultValidatorSetting },
    { name: 'hiragana', model: DefaultValidatorSetting },
    { name: 'katakana', model: DefaultValidatorSetting },
    { name: 'other_characters', model: DefaultValidatorSetting }
  ];

  var Validators = Backbone.Model.extend({
    defaults: {
      numerics: null,
      alphabets: null,
      hiragana: null,
      katakana: null,
      other_characters: null
    },

    initialize: function (_attributes, options) {
      var self = this; 
      _.each(validatorDefs, function (validatorDef) {
        var validatorSetting = self.attributes[validatorDef.name];
        if (validatorSetting === null) {
          validatorSetting = new validatorDef.model({}, options);
          if (validatorSetting.get('enabled') === null) {
            validatorSetting.set('enabled', typeof validatorDef.enabledByDefault == 'boolean' ? validatorDef.enabledByDefault: true);
          }
          self.set(validatorDef.name, validatorSetting, options);
        }
      });
      _.each(this.attributes, function (validatorSetting, k) {
        validatorSetting.on('change', function (_, current) {
          self.trigger('change:' + k, self, current, options);
          self.trigger('change', self, options);
        });
      });
    },

    validate: function (attributes, options) {
      var enabled = false;
      for (var name in attributes) {
        if (!attributes.hasOwnProperty(name))
          continue;
        if (attributes[name] == null)
          return;
        if (attributes[name].get('enabled'))
          enabled = true; 
      }
      if (!enabled) {
        return translations['ja']['message']['must_choose_at_least_one_validator_type'];
      }
    },

    parse: function (resp, options) {
      resp = resp || {};
      _.each(validatorDefs, function (validatorDef) {
        var validatorSetting = new validatorDef.model(resp[validatorDef.name] || {}, options);
        if (validatorSetting.get('enabled') === null)
          validatorSetting.set('enabled', typeof validatorDef.enabledByDefault == 'boolean' ? validatorDef.enabledByDefault: true);
        resp[validatorDef.name] = validatorSetting;
      });
      return resp;
    }
  });

  function compile_predicate(s) {
    new dynpredicate.Parser(new dynpredicate.Tokenizer(s)).parse();
  }

  var Field = Backbone.Model.extend({
    defaults: {
      index: 0,
      name: '',
      display_name: '',
      kind: 'text',
      description: '',
      note: '',
      required: false,
      show_on_entry: true,
      show_in_orderreview: true,
      edit_in_orderreview: false,
      activation_conditions: '',
      max_length: null,
      validators: null,
      choices: null
    },

    _errors: null,

    initialize: function (attributes, options) {
      var self = this;
      this.attributes['choices'] = new Choices(this.attributes['choices'], options);
      this.attributes['validators'] = new Validators(this.attributes['validators'], options);
      this.attributes['validators'].on('change', function (item, options) {
        self.trigger('change:validators', self, item, options); 
        self.trigger('change', self, options); 
        if (self.validate(self.attributes, options))
          self.trigger('error');
      });
      if (this.attributes['max_length'] === null)
        this.attributes['max_length'] = this.max_length_limit();
      if (config['make_name_idential_to_display_name']) {
        this.on('change:display_name', function () {
          this.set('name', this.get('display_name'));
        }, this)
      }
    },

    max_length_limit: function () {
      return this.attributes.kind == 'textarea' ? 2048: 150;
    },

    validate: function (attributes, options) {
      var max_length_limit = this.max_length_limit();
      var errors = {};
      if (attributes['max_length'] < 1) {
        errors['max_length'] = translations['ja']['message']['must_be_equal_to_or_greater_than'].replace('{}', '' + 1);
      } else if (attributes['max_length'] > max_length_limit) {
        errors['max_length'] = translations['ja']['message']['must_be_equal_to_or_less_than'].replace('{}', '' + max_length_limit);
      } else if (isNaN(attributes['max_length'])) {
        errors['max_length'] = translations['ja']['message']['must_be_a_number'].replace('{}', '' + max_length_limit);
      }
      if (attributes['activation_conditions']) {
        try {
          compile_predicate(attributes['activation_conditions']);
        } catch (e) {
          errors['activation_conditions'] = e.message;
        }
      }
      if (attributes['validators'] !== null) {
        var e = attributes['validators'].validate(attributes['validators'].attributes, options);
        if (e)
          errors['validators'] = e;
      }
      if (!_.isEmpty(errors)) {
        this._errors = errors;
        return errors;
      }
    }
  });

  var FieldView = Backbone.View.extend({
    tagName: 'tr',
    handler_factories: handler_factories,
    configuration_form_content_view: null,
    preview_view: null,

    initialize: function () {
      this.model.on("change:kind", this.render, this);
      this.model.on("change:index", function () {
        this.$el.find('> td.index > div.index').text(this.model.get('index'));
      }, this);
      this.model.on("change:description", function () {
        this.$el.find('> td.preview > div.description').html(this.model.get('description'));
      }, this);
      this.model.on("change:note", function () {
        this.$el.find('> td.preview > div.note').html(this.model.get('note'));
      }, this);
      this.model.on("change:show_on_entry", function () {
        this.$el.find('> td.name-and-kind :checkbox[name="show_on_entry"]').attr('checked', this.model.get('show_on_entry') ? 'checked': null);
      }, this);
      this.model.on("change:show_in_orderreview", function () {
        this.$el.find('> td.name-and-kind :checkbox[name="show_in_orderreview"]').attr('checked', this.model.get('show_in_orderreview') ? 'checked': null);
      }, this);
      this.model.on("change:edit_in_orderreview", function () {
        this.$el.find('> td.name-and-kind :checkbox[name="edit_in_orderreview"]').attr('checked', this.model.get('edit_in_orderreview') ? 'checked': null);
      }, this);
      this.model.on("change", function (model) {
        this.$el.removeClass("error");
        this.$el.find('.control-group').removeClass('error');
      }, this);
      this.model.on("error", function (model, errors) {
        var self = this;
        _.each(errors, function (error, k) {
          self.$el.find('*[name="' + k + '"]').closest(".control-group").addClass('error');
        });
        this.$el.addClass("error");
      }, this);
    },

    render_index: function () {
      var self = this;
      var $btn_remove =
        $('<button style="white-space: nowrap" class="action-remove btn btn-small btn-danger"></button>')
        .text(translations['ja']['remove'])
        .on('click', function () {
          self.trigger('remove');
        });
      var $btn_move_up = 
        $('<button style="white-space: nowrap" class="action-remove btn btn-small"><i class="icon-arrow-up"></i></button>')
        .on('click', function () {
          self.trigger('move_up');
        });
      var $btn_move_down = 
        $('<button style="white-space: nowrap" class="action-remove btn btn-small"><i class="icon-arrow-down"></i></button>')
        .on('click', function () {
          self.trigger('move_down');
        });
      return $('<div class="index"></div>').text(this.model.get('index'))
        .add(
          $('<div class="actions"></div>')
          .append($btn_move_up)
          .append($btn_move_down)
          .append($btn_remove)
        );
    },

    render_kind_label: function (label) {
      return translations['ja']['kind'][label]
    },

    render_kind_selector: function () {
      var self = this;
      var retval = $('<select style="margin-left:8px; margin-bottom:0; width:12em;"></select>');
      var selected_kind = this.model.get('kind');
      _.map(self.handler_factories, function (v, k) {
        retval.append(
          $('<option></option>')
            .attr('value', k)
            .text(self.render_kind_label(k))
            .attr('selected', selected_kind == k ? 'selected': null)
        );
      });
      retval.on('change', function () {
        self.model.set('kind', retval.val());
      });
      return retval;
    },

    render_display_name: function () {
      var retval = $('<input type="text" name="display_name" style="width:10em;margin-bottom:0; " />')
        .attr("placeholder", translations['ja']['placeholder']['display_name'])
        .val(this.model.get('display_name'));
      var self = this;
      retval.on('change', function () {
        self.model.set('display_name', this.value);
        if (self.model.get('name') == '')
          self.model.set('name', this.value);
      });
      return retval;
    },

    render_description: function () {
      var retval = $('<textarea name="description" style="width:90%; height:49px"></textarea>')
        .attr("placeholder", translations['ja']['placeholder']['description'])
        .text(this.model.get('description'));
      var self = this;
      retval.on('change', function () { self.model.set('description', this.value); });
      return retval;
    },

    render_note: function () {
      var retval = $('<textarea name="note" style="width:90%; height:49px"></textarea>')
        .attr("placeholder", translations['ja']['placeholder']['note'])
        .text(this.model.get('note'));
      var self = this;
      retval.on('change', function () { self.model.set('note', this.value); });
      return retval;
    },

    render_preview: function () {
      return $('<div class="description"></div>').html(this.model.get('description'))
        .add($('<div></div>').append(this.preview_view.$el))
        .add($('<div class="note"></div>').html(this.model.get('note')));
    },

    render_requisite_checkbox: function () {
      var self = this;
      return $('<label class="checkbox inline" style="margin-left:8px"></label>')
        .text(translations['ja']['required'])
        .prepend(
          $('<input name="required" type="checkbox" />')
          .attr('checked', this.model.get('required') ? 'checked': null)
          .on('click', function () { self.model.set('required', this.checked); })
        );
    },

    render_activation_conditions: function () {
      var self = this;
      return (
          $('<label class="control-label"></label>')
          .text(translations['ja']['activation_conditions'])
          .add(
            $('<input type="text" name="activation_conditions" />')
            .attr("placeholder", translations['ja']['placeholder']['conditional_expressions'])
            .attr('value', this.model.get('activation_conditions'))
            .on('change', function () { self.model.set('activation_conditions', this.value); })
          )
        );
    },

    render_show_on_entry: function () {
      var self = this;
      return $('<label class="checkbox inline"></label>')
          .text(translations['ja']['show_on_entry'])
          .prepend(
            $('<input type="checkbox" name="show_on_entry" />')
            .attr('checked', this.model.get('show_on_entry') ? 'checked': null)
            .on('click', function () { self.model.set('show_on_entry', this.checked); })
          );
    },

    render_show_in_orderreview: function () {
      var self = this;
      return $('<label class="checkbox inline"></label>')
          .text(translations['ja']['show_in_orderreview'])
          .prepend(
            $('<input type="checkbox" name="show_in_orderreview" />')
            .attr('checked', this.model.get('show_in_orderreview') ? 'checked': null)
            .on('click', function () { self.model.set('show_in_orderreview', this.checked); })
          );
    },

    render_edit_in_orderreview: function () {
      var self = this;
      return $('<label class="checkbox inline"></label>')
          .text(translations['ja']['edit_in_orderreview'])
          .prepend(
            $('<input type="checkbox" name="edit_in_orderreview" />')
            .attr('checked', this.model.get('edit_in_orderreview') ? 'checked': null)
            .on('click', function () {
                self.model.set('edit_in_orderreview', this.checked);
                if (this.checked)
                    self.model.set('show_in_orderreview', true);
            })
          );
    },

    refresh_subviews: function () {
      if (this.configuration_form_content_view != null) {
        this.configuration_form_content_view.remove();
        this.configuration_form_content_view.$el.remove();
      }
      if (this.preview_view != null) {
        this.preview_view.remove();
        this.preview_view.$el.remove();
      }
      var handler = this.handler_factories[this.model.get('kind')]();
      this.configuration_form_content_view = handler.configuration_form_content_view(this.model, this.$el);
      this.preview_view = handler.preview_view(this.model);

      this.configuration_form_content_view.render();
      this.preview_view.render();
    },

    render: function () {
      var $preview, $configuration;
      this.$el
        .empty()
        .append($('<td class="index"></td>').append(this.render_index()))
        .append(
          $('<td class="name-and-kind"></td>')
          .append(
            $('<div class="controls controls-row"></div>')
            .append(this.render_display_name())
            .append(this.render_kind_selector())
            .append(this.render_requisite_checkbox())
          )
          .append(
            $('<div class="controls control-row" style="height:2.5em"></div>')
            .append(this.render_show_on_entry())
            .append(this.render_show_in_orderreview())
            .append(this.render_edit_in_orderreview())
          )
          .append(
            $('<div class="form-inline control-group" style="margin-bottom: 6px"></div>')
            .append(this.render_activation_conditions())
          )
          .append(
            $('<div class="description"></div>')
            .append(this.render_description())
          )
          .append(
            $('<div class="note"></div>')
            .append(this.render_note())
          )
        )
        .append($configuration = $('<td class="configuration"></td>'))
        .append($preview = $('<td class="preview"></td>'))
        ;
        this.refresh_subviews();
        $configuration.append(this.configuration_form_content_view.$el);
        $preview.append(this.render_preview());
      return this;
    }
  });

  var TextConfigurationView = Backbone.View.extend({
    initialize: function () {
    },

    render_max_length: function () {
      var self = this;
      return $('<label class="control-label"></label>').text(translations['ja']['max_length'])
        .add(
          $('<input type="text" name="max_length" class="input-small" />')
          .val(this.model.get('max_length'))
          .on('change', function () {
            self.model.set('max_length', parseIntExactly(this.value));
          })
        );
    },

    render_validator_settings: function () {
      var self = this;
      var retval = $('<label class="control-label"></label>').text(translations['ja']['validators']);
      var $div = $('<div class="controls"></div>');
      var settings = self.model.get('validators');
      $.each(validatorDefs, function (_, validatorDef) {
        var setting = settings.get(validatorDef.name);
        $div.append(
          $('<label class="checkbox control-label"></label>')
          .append(
            $('<input type="checkbox" />')
            .attr('name', 'validators-' + self.model.cid)
            .attr('value', validatorDef.name)
            .attr('checked', setting.get('enabled'))
            .on('change', function () {
              setting.set('enabled', this.checked);
            })
          )
          .append(document.createTextNode(translations['ja']['validator'][validatorDef.name]))
        )
      });
      retval = retval.add($div);
      return retval;
    },

    render: function () {
      var self = this;
      this.$el
        .empty()
        .append($('<div class="control-group"></div>').append(this.render_max_length()))
        .append($('<div class="control-group"></div>').append(this.render_validator_settings()));
      return this;
    }
  });

  var SelectConfigurationView = Backbone.View.extend({
    choices: null,

    initialize: function () {
      this.choices = {};

      this.on('new', this.add_unbound_view, this);
      var choices = this.model.get('choices');
      choices.on('add', this.get_choice_view, this);
      choices.on('remove', this.on_remove_choice, this);
      choices.on('reset', this.render, this);
      if (choices.length == 0) {
        this.add_unbound_view();
      }
    },

    get_choice_view: function (choice) {
      var desc = this.choices[choice.cid];
      var bound = this.model.get('choices').contains(choice);
      if (desc === void(0)) {
        var choice_view = new ChoiceView({ model: choice });
        desc = this.choices[choice.cid] = { choice_view: choice_view, bound: null };
        choice_view.render().$el.insertBefore(this.$el.find('> tbody > tr.last'));
      }
      if (bound != desc.bound) {
        desc.bound = bound;
        this.bind_events(desc.choice_view, bound);
      }
      return desc.choice_view;
    },

    bind_events: function (choice_view, bound) {
      choice_view.on('remove', null, this);
      if (bound) {
        choice_view.on('remove', function () {
          this.model.get('choices').remove(choice_view.model);
        }, this);
      } else {
        choice_view.on('remove', function () {
          this.remove_choice_view(choice_view);
        }, this);
      }
    },

    remove_choice_view: function (choice_view) {
      choice_view.remove();
      choice_view.$el.remove();
      delete this.choices[choice_view.model.cid];
    },

    on_remove_choice: function (choice) {
      var desc = this.choices[choice.cid];
      if (desc !== void(0)) {
        this.remove_choice_view(desc.choice_view);
      }
    },

    add_unbound_view: function () {
      var unbound_choice_view = this.get_choice_view(new Choice({ label: '', value: '' }));
      unbound_choice_view.model.on('change', function () {
        unbound_choice_view.model.off('change', arguments.callee, this);
        this.model.get('choices').add(unbound_choice_view.model);
      }, this);
    },

    clear: function () {
      var bounds = [];
      _.map(this.choices, function (v, k) {
        if (v.bound) {
          v.choice_view.remove();
          v.choice_view.$el.remove();
          bounds.push(k);
        }
      });
      var self = this;
      _.each(bounds, function (k) {
        delete self.choices[k]; 
      });
    },

    render: function () {
      this.clear();
      var self = this;
      this.model.get('choices').each(function (choice) {
        var choice_view = self.get_choice_view(choice);
        choice_view.render().$el.insertBefore(self.$el.find('> tbody > tr.last'));
      });
      return this;
    }
  });

  var DateConfigurationView = Backbone.View.extend({
    initialize: function (options) {},

    render: function () {
      return this;
    }
  });

  var FieldCollection = Backbone.Collection.extend({
    model: Field,
 
    initialize: function () {
      this.on('add', function (model) {
        model.set('index', this.length - 1);
      }, this);
      this.on('remove', function (model) {
        for (var i = model.get('index'); i < this.length; i++) {
          this.at(i).set('index', i);
        }
      }, this);
    },

    swap: function (a, b, options) {
      var index_a = this.indexOf(a), index_b = this.indexOf(b);
      if (index_a < 0 || index_b < 0 || index_a == index_b)
        return false;
      this.models[index_a] = b;
      this.models[index_b] = a;
      var options = options ? _.clone(options): {};
      options.primary = true;
      options.other = b;
      options.index = index_b;
      options.otherIndex = index_a;
      a.trigger("swap", a, this, options);
      options.primary = false;
      options.other = a;
      options.index = index_a;
      options.otherIndex = index_b;
      b.trigger("swap", b, this, options);
      return true;
    },

    _onModelEvent: function (event, model, collection, options) {
      if (event == 'swap') {
        if (collection != this)
          return;
        if (options.primary)
          this.trigger.apply(this, arguments);
        return;
      }
      Backbone.Collection.prototype._onModelEvent.apply(this, arguments);
    }
  });

  var FieldCollectionView = Backbone.View.extend({
    fields: {},

    initialize: function () {
      this.model.on('add', this.get_field_view, this);
      this.model.on('remove', this.remove_field_view, this);
      this.model.on('reset', this.render, this);
      this.model.on('swap', this.swap, this);
    },

    get_field_view: function (field) {
      var field_view = this.fields[field.cid];
      if (field_view === void(0)) {
        field_view = new FieldView({ model: field });
        this.fields[field.cid] = field_view;
        field_view.render().$el.insertBefore(this.$el.find('> tbody > tr.last'));
        field_view.on('remove', function () { this.model.remove(field); }, this);
        field_view.on("move_up", function () {
          var i = field.get('index');
          if (i > 0) {
            var prev_field = this.model.at(i - 1);
            this.model.swap(prev_field, field);
          }
        }, this);
        field_view.on("move_down", function () {
          var i = field.get('index');
          if (i < this.model.length - 1) {
            var next_field = this.model.at(i + 1);
            this.model.swap(next_field, field);
          }
        }, this);
      }
      return field_view;
    },

    remove_field_view: function (field) {
      var field_view = this.fields[field.cid];
      if (field_view !== void(0)) {
        field_view.remove();
        field_view.$el.remove();
        delete this.fields[field.cid];
      }
    },

    clear: function () {
      _.map(this.fields, function (v, k) {
        v.remove();
        v.$el.remove();
      });
      this.fields = {} 
    },

    swap: function (model, _, options) {
      var other = options.other;
      model.set('index', options.index);
      other.set('index', options.otherIndex);

      var anterior, posterior;
      if (options.index > options.otherIndex) {
        anterior = model;
        posterior = options.other;
      } else {
        anterior = options.other;
        posterior = model;
      }

      var anterior_view = this.get_field_view(anterior),
          posterior_view = this.get_field_view(posterior);
      var anterior_prev_sibling = anterior_view.$el.prev(),
          posterior_next_sibling = posterior_view.$el.next();
      if (anterior_prev_sibling.length != 0)
        posterior_view.$el.insertAfter(anterior_prev_sibling);
      else
        posterior_view.$el.prependTo(posterior_view.$el.parent());
      anterior_view.$el.insertBefore(posterior_next_sibling);
    },

    render: function () {
      this.clear();
      var self = this;
      this.model.each(function (field) {
        var field_view = self.get_field_view(field);
        field_view.render().$el.insertBefore(self.$el.find('> tbody > tr.last'))
      });
      return this;
    }
  });

  return function (_elements) {
    var fields = new FieldCollection();
    var fieldCollectionView = new FieldCollectionView({
      model: fields,
      el: _elements.table[0]
    });
    _elements.table.find('> tbody > tr:not(.last)').remove();
    function new_row() {
      var model = new Field();
      fields.add(model);
    }

    _elements.add_new_field_btn.on('click', function () { new_row(); return false });
    return fields;
  };
});
/*
 * vim: sts=2 sw=2 ts=2 et
 */
