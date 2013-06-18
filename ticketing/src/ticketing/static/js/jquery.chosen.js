
(function () {
    var d, e, c, a;
    var b = function (f, g) {
        return function () {
            return f.apply(g, arguments)
        }
    };
    a = this;
    d = jQuery;
    d.fn.extend({
        chosen: function (f) {
            if (d.browser.msie && parseInt(d.browser.version) < 7) {
                return this.show()
            }
            return d(this).each(function (g) {
                if (!(d(this)).hasClass("chzn-done")) {
                    return new e(this, f)
                }
            })
        }
    });
    e = (function () {
        function f(g, h) {
            this.form_field = g;
            this.options = h != null ? h : {};
            if (this.options.single_only && this.form_field.multiple) {
                d(g).show();
                return false
            }
            this.set_default_values();
            this.form_field_jq = d(this.form_field);
            this.is_multiple = this.form_field.multiple;
            this.is_rtl = this.form_field_jq.hasClass("chzn-rtl");
            this.default_text_default = " ";
            this.set_up_html();
            this.register_observers();
            this.form_field_jq.addClass("chzn-done")
        }
        f.prototype.set_default_values = function () {
            this.click_test_action = b(function (g) {
                return this.test_active_click(g)
            }, this);
            this.activate_action = b(function (g) {
                return this.activate_field(g)
            }, this);
            this.active_field = false;
            this.mouse_on_container = false;
            this.results_showing = false;
            this.result_highlighted = null;
            this.result_single_selected = null;
            this.allow_single_deselect = (this.options.allow_single_deselect != null) && this.form_field.options[0].text === "" ? this.options.allow_single_deselect : false;
            this.disable_search_threshold = this.options.disable_search_threshold || 0;
            this.choices = 0;
            return this.results_none_found = this.options.no_results_text || "No results match"
        };
        f.prototype.set_up_html = function () {
            var j, i, h, g;
            this.container_id = this.form_field.id.length ? this.form_field.id.replace(/(:|\.)/g, "_") : this.generate_field_id();
            this.container_id += "_chzn";
            this.f_width = this.form_field_jq.outerWidth();
            this.default_text = this.form_field_jq.data("placeholder") ? this.form_field_jq.data("placeholder") : this.default_text_default;
            j = d("<div />", {
                id: this.container_id,
                "class": "chzn-container" + (this.is_rtl ? " chzn-rtl" : ""),
                style: "width: " + this.f_width + "px;"
            });
            if (this.is_multiple) {
                j.html('<ul class="chzn-choices"><li class="search-field"><input type="text" value="' + this.default_text + '" class="default" autocomplete="off" style="width:25px;" /></li></ul><div class="chzn-drop" style="left:-9000px;"><ul class="chzn-results"></ul></div>')
            } else {
                j.html('<a href="javascript:void(0)" class="chzn-single"><span>' + this.default_text + '</span><div><b></b></div></a><div class="chzn-drop" style="left:-9000px;"><div class="chzn-search"><input type="text" autocomplete="off" /></div><ul class="chzn-results"></ul></div>');
                if (this.options.no_search) {
                    j.find("div.chzn-search").hide()
                }
            }
            this.form_field_jq.hide().after(j);
            this.container = d("#" + this.container_id);
            this.container.addClass("chzn-container-" + (this.is_multiple ? "multi" : "single"));
            if (!this.is_multiple && this.form_field.options.length <= this.disable_search_threshold) {
                this.container.addClass("chzn-container-single-nosearch")
            }
            this.dropdown = this.container.find("div.chzn-drop").first();
            i = this.container.height();
            h = this.f_width - c(this.dropdown);
            this.dropdown.css({
                width: h + "px",
                top: i + "px"
            });
            this.search_field = this.container.find("input").first();
            this.search_results = this.container.find("ul.chzn-results").first();
            this.search_field_scale();
            this.search_no_results = this.container.find("li.no-results").first();
            if (this.is_multiple) {
                this.search_choices = this.container.find("ul.chzn-choices").first();
                this.search_container = this.container.find("li.search-field").first()
            } else {
                this.search_container = this.container.find("div.chzn-search").first();
                this.selected_item = this.container.find(".chzn-single").first();
                g = h - c(this.search_container) - c(this.search_field);
                this.search_field.css({
                    width: g + "px"
                })
            }
            this.results_build();
            return this.set_tab_index()
        };
        f.prototype.register_observers = function () {
            this.container.mousedown(b(function (g) {
                return this.container_mousedown(g)
            }, this));
            this.container.mouseup(b(function (g) {
                return this.container_mouseup(g)
            }, this));
            this.container.mouseenter(b(function (g) {
                return this.mouse_enter(g)
            }, this));
            this.container.mouseleave(b(function (g) {
                return this.mouse_leave(g)
            }, this));
            this.search_results.mouseup(b(function (g) {
                return this.search_results_mouseup(g)
            }, this));
            this.search_results.mouseover(b(function (g) {
                return this.search_results_mouseover(g)
            }, this));
            this.search_results.mouseout(b(function (g) {
                return this.search_results_mouseout(g)
            }, this));
            this.form_field_jq.bind("liszt:updated", b(function (g) {
                return this.results_update_field(g)
            }, this));
            this.search_field.blur(b(function (g) {
                return this.input_blur(g)
            }, this));
            this.search_field.keypress(b(function (g) {
                return this.keypress_checker(g)
            }, this));
            this.search_field.keyup(b(function (g) {
                return this.keyup_checker(g)
            }, this));
            this.search_field.keydown(b(function (g) {
                return this.keydown_checker(g)
            }, this));
            if (this.is_multiple) {
                this.search_choices.click(b(function (g) {
                    return this.choices_click(g)
                }, this));
                return this.search_field.focus(b(function (g) {
                    return this.input_focus(g)
                }, this))
            }
        };
        f.prototype.search_field_disabled = function () {
            this.is_disabled = this.form_field_jq.attr("disabled");
            if (this.is_disabled) {
                this.container.addClass("chzn-disabled");
                this.search_field.attr("disabled", true);
                if (!this.is_multiple) {
                    this.selected_item.unbind("focus", this.activate_action)
                }
                return this.close_field()
            } else {
                this.container.removeClass("chzn-disabled");
                this.search_field.attr("disabled", false);
                if (!this.is_multiple) {
                    return this.selected_item.bind("focus", this.activate_action)
                }
            }
        };
        f.prototype.container_mousedown = function (g) {
            var h;
            if (!this.is_disabled) {
                h = g != null ? (d(g.target)).hasClass("search-choice-close") : false;
                if (g && g.type === "mousedown") {
                    g.stopPropagation()
                }
                if (!this.pending_destroy_click && !h) {
                    if (!this.active_field) {
                        if (this.is_multiple) {
                            this.search_field.val("")
                        }
                        d(document).click(this.click_test_action);
                        this.results_show()
                    } else {
                        if (!this.is_multiple && g && (d(g.target) === this.selected_item || d(g.target).parents("a.chzn-single").length)) {
                            g.preventDefault();
                            this.results_toggle()
                        }
                    }
                    return this.activate_field()
                } else {
                    return this.pending_destroy_click = false
                }
            }
        };
        f.prototype.container_mouseup = function (g) {
            if (g.target.nodeName === "ABBR") {
                return this.results_reset(g)
            }
        };
        f.prototype.mouse_enter = function () {
            return this.mouse_on_container = true
        };
        f.prototype.mouse_leave = function () {
            return this.mouse_on_container = false
        };
        f.prototype.input_focus = function (g) {
            if (!this.active_field) {
                return setTimeout((b(function () {
                    return this.container_mousedown()
                }, this)), 50)
            }
        };
        f.prototype.input_blur = function (g) {
            if (!this.mouse_on_container) {
                this.active_field = false;
                return setTimeout((b(function () {
                    return this.blur_test()
                }, this)), 100)
            }
        };
        f.prototype.blur_test = function (g) {
            if (!this.active_field && this.container.hasClass("chzn-container-active")) {
                return this.close_field()
            }
        };
        f.prototype.close_field = function () {
            d(document).unbind("click", this.click_test_action);
            if (!this.is_multiple) {
                this.selected_item.attr("tabindex", this.search_field.attr("tabindex"));
                this.search_field.attr("tabindex", -1)
            }
            this.active_field = false;
            this.results_hide();
            this.container.removeClass("chzn-container-active");
            this.winnow_results_clear();
            this.clear_backstroke();
            this.show_search_field_default();
            return this.search_field_scale()
        };
        f.prototype.activate_field = function () {
            if (!this.is_multiple && !this.active_field) {
                this.search_field.attr("tabindex", this.selected_item.attr("tabindex"));
                this.selected_item.attr("tabindex", -1)
            }
            this.container.addClass("chzn-container-active");
            this.active_field = true;
            this.search_field.val(this.search_field.val());
            return this.search_field.focus()
        };
        f.prototype.test_active_click = function (g) {
            if (d(g.target).parents("#" + this.container_id).length) {
                return this.active_field = true
            } else {
                return this.close_field()
            }
        };
        f.prototype.results_build = function () {
            var j, m, i, l, g, k;
            i = new Date();
            this.parsing = true;
            this.results_data = a.SelectParser.select_to_array(this.form_field);
            if (this.is_multiple && this.choices > 0) {
                this.search_choices.find("li.search-choice").remove();
                this.choices = 0
            } else {
                if (!this.is_multiple) {
                    if (this.default_text && this.default_text !== " ") {
                        this.selected_item.find("span").first().text(this.default_text)
                    } else {
                        this.selected_item.find("span").first().html("&nbsp;")
                    }
                }
            }
            j = "";
            k = this.results_data;
            for (l = 0, g = k.length; l < g; l++) {
                m = k[l];
                if (m.group) {
                    j += this.result_add_group(m)
                } else {
                    j += this.result_add_option(m);
                    if (m.selected && this.is_multiple) {
                        this.choice_build(m)
                    } else {
                        if (m.selected && !this.is_multiple) {
                            if (m.text && m.text !== " ") {
                                var h = "";
                                if (m.icon) {
                                    h += '<img src="' + m.icon + '" class="chosen-icon"/>'
                                }
                                h += m.html;
                                this.selected_item.find("span").html(h)
                            } else {
                                if (this.default_text && this.default_text !== " ") {
                                    this.selected_item.find("span").first().html('<span class="chzn-default">' + this.default_text + "</span>")
                                } else {
                                    this.selected_item.find("span").html("&nbsp;")
                                }
                            } if (this.allow_single_deselect) {
                                this.selected_item.find("span").first().after('<abbr class="search-choice-close"></abbr>')
                            }
                        }
                    }
                }
            }
            this.search_field_disabled();
            this.show_search_field_default();
            this.search_field_scale();
            this.search_results.html(j);
            return this.parsing = false
        };
        f.prototype.result_add_group = function (g) {
            if (!g.disabled) {
                g.dom_id = this.container_id + "_g_" + g.array_index;
                return '<li id="' + g.dom_id + '" class="group-result">' + d("<div />").text(g.label).html() + "</li>"
            } else {
                return ""
            }
        };
        f.prototype.result_add_option = function (j) {
            var h, i, g;
            if (!j.disabled) {
                j.dom_id = this.container_id + "_o_" + j.array_index;
                h = j.selected && this.is_multiple ? [] : ["active-result"];
                if (j.selected) {
                    h.push("result-selected")
                }
                if (j.group_array_index != null) {
                    h.push("group-option")
                }
                if (j.classes !== "") {
                    h.push(j.classes)
                }
                i = j.style.cssText !== "" ? ' style="' + j.style + '"' : "";
                g = "";
                if (j.icon) {
                    g += '<img src="' + j.icon + '" class="chosen-icon"/>'
                }
                g += j.html;
                return '<li id="' + j.dom_id + '" class="' + h.join(" ") + '"' + i + ">" + g + "</li>"
            } else {
                return ""
            }
        };
        f.prototype.results_update_field = function () {
            this.result_clear_highlight();
            this.result_single_selected = null;
            return this.results_build()
        };
        f.prototype.result_do_highlight = function (h) {
            var l, k, i, j, g;
            if (h.length) {
                this.result_clear_highlight();
                this.result_highlight = h;
                this.result_highlight.addClass("highlighted");
                i = parseInt(this.search_results.css("maxHeight"), 10);
                g = this.search_results.scrollTop();
                j = i + g;
                k = this.result_highlight.position().top + this.search_results.scrollTop();
                l = k + this.result_highlight.outerHeight();
                if (l >= j) {
                    return this.search_results.scrollTop((l - i) > 0 ? l - i : 0)
                } else {
                    if (k < g) {
                        return this.search_results.scrollTop(k)
                    }
                }
            }
        };
        f.prototype.result_clear_highlight = function () {
            if (this.result_highlight) {
                this.result_highlight.removeClass("highlighted")
            }
            return this.result_highlight = null
        };
        f.prototype.results_toggle = function () {
            if (this.results_showing) {
                return this.results_hide()
            } else {
                return this.results_show()
            }
        };
        f.prototype.results_show = function () {
            var g;
            if (!this.is_multiple) {
                this.selected_item.addClass("chzn-single-with-drop");
                if (this.result_single_selected) {
                    this.result_do_highlight(this.result_single_selected)
                }
            }
            g = this.is_multiple ? this.container.height() : this.container.height() - 1;
            this.dropdown.css({
                top: g + "px",
                left: 0
            });
            this.results_showing = true;
            this.search_field.focus();
            this.search_field.val(this.search_field.val());
            return this.winnow_results()
        };
        f.prototype.results_hide = function () {
            if (!this.is_multiple) {
                this.selected_item.removeClass("chzn-single-with-drop")
            }
            this.result_clear_highlight();
            this.dropdown.css({
                left: "-9000px"
            });
            return this.results_showing = false
        };
        f.prototype.set_tab_index = function (h) {
            var g;
            if (this.form_field_jq.attr("tabindex")) {
                g = this.form_field_jq.attr("tabindex");
                this.form_field_jq.attr("tabindex", -1);
                if (this.is_multiple) {
                    return this.search_field.attr("tabindex", g)
                } else {
                    this.selected_item.attr("tabindex", g);
                    return this.search_field.attr("tabindex", -1)
                }
            }
        };
        f.prototype.show_search_field_default = function () {
            if (this.is_multiple && this.choices < 1 && !this.active_field) {
                this.search_field.val(this.default_text);
                return this.search_field.addClass("default")
            } else {
                this.search_field.val("");
                return this.search_field.removeClass("default")
            }
        };
        f.prototype.search_results_mouseup = function (g) {
            var h;
            h = d(g.target).hasClass("active-result") ? d(g.target) : d(g.target).parents(".active-result").first();
            if (h.length) {
                this.result_highlight = h;
                return this.result_select(g)
            }
        };
        f.prototype.search_results_mouseover = function (g) {
            var h;
            h = d(g.target).hasClass("active-result") ? d(g.target) : d(g.target).parents(".active-result").first();
            if (h) {
                return this.result_do_highlight(h)
            }
        };
        f.prototype.search_results_mouseout = function (g) {
            if (d(g.target).hasClass("active-result" || d(g.target).parents(".active-result").first())) {
                return this.result_clear_highlight()
            }
        };
        f.prototype.choices_click = function (g) {
            g.preventDefault();
            if (this.active_field && !(d(g.target).hasClass("search-choice" || d(g.target).parents(".search-choice").first)) && !this.results_showing) {
                return this.results_show()
            }
        };
        f.prototype.choice_build = function (j) {
            var g, i;
            g = this.container_id + "_c_" + j.array_index;
            this.choices += 1;
            var h = j.html;
            if (j.icon) {
                h = '<img src="' + j.icon + '" class="chosen-icon" />' + h
            }
            this.search_container.before('<li class="search-choice" id="' + g + '"><span>' + h + '</span><a href="javascript:void(0)" class="search-choice-close" rel="' + j.array_index + '"></a></li>');
            i = d("#" + g).find("a").first();
            return i.click(b(function (k) {
                return this.choice_destroy_link_click(k)
            }, this))
        };
        f.prototype.choice_destroy_link_click = function (g) {
            g.preventDefault();
            if (!this.is_disabled) {
                this.pending_destroy_click = true;
                return this.choice_destroy(d(g.target))
            } else {
                return g.stopPropagation
            }
        };
        f.prototype.choice_destroy = function (g) {
            this.choices -= 1;
            this.show_search_field_default();
            if (this.is_multiple && this.choices > 0 && this.search_field.val().length < 1) {
                this.results_hide()
            }
            this.result_deselect(g.attr("rel"));
            return g.parents("li").first().remove()
        };
        f.prototype.results_reset = function (g) {
            this.form_field.options[0].selected = true;
            this.selected_item.find("span").text(this.default_text);
            this.show_search_field_default();
            d(g.target).remove();
            this.form_field_jq.trigger("change");
            if (this.active_field) {
                return this.results_hide()
            }
        };
        f.prototype.result_select = function (h) {
            var l, k, j, g;
            if (this.result_highlight) {
                l = this.result_highlight;
                k = l.attr("id");
                this.result_clear_highlight();
                if (this.is_multiple) {
                    this.result_deactivate(l)
                } else {
                    this.search_results.find(".result-selected").removeClass("result-selected");
                    this.result_single_selected = l
                }
                l.addClass("result-selected");
                g = k.substr(k.lastIndexOf("_") + 1);
                j = this.results_data[g];
                j.selected = true;
                this.form_field.options[j.options_index].selected = true;
                if (this.is_multiple) {
                    this.choice_build(j)
                } else {
                    if (j.text && j.text !== " ") {
                        var i = j.icon ? '<img src="' + j.icon + '" class="chosen-icon">' + j.html : j.html;
                        this.selected_item.find("span").first().html(i)
                    } else {
                        if (this.default_text && this.default_text !== " ") {
                            this.selected_item.find("span").first().html('<span class="chzn-default">' + this.default_text + "</span>")
                        } else {
                            this.selected_item.find("span").first().html("&nbsp;")
                        }
                    } if (this.allow_single_deselect) {
                        this.selected_item.find("span").first().after('<abbr class="search-choice-close"></abbr>')
                    }
                } if (!(h.metaKey && this.is_multiple)) {
                    this.results_hide()
                }
                this.search_field.val("");
                this.form_field_jq.trigger("change");
                return this.search_field_scale()
            }
        };
        f.prototype.result_activate = function (g) {
            return g.addClass("active-result")
        };
        f.prototype.result_deactivate = function (g) {
            return g.removeClass("active-result")
        };
        f.prototype.result_deselect = function (i) {
            var g, h;
            h = this.results_data[i];
            h.selected = false;
            this.form_field.options[h.options_index].selected = false;
            g = d("#" + this.container_id + "_o_" + i);
            g.removeClass("result-selected").addClass("active-result").show();
            this.result_clear_highlight();
            this.winnow_results();
            this.form_field_jq.trigger("change");
            return this.search_field_scale()
        };
        f.prototype.results_search = function (g) {
            if (this.results_showing) {
                return this.winnow_results()
            } else {
                return this.results_show()
            }
        };
        f.prototype.is_best_match = function (h, l) {
            if (h.indexOf(" ") == -1) {
                return false
            }
            var k = h.split(" ");
            for (var j = 0; j < k.length; j++) {
                var m = k[j];
                var g = m.match(l);
                if (g && (g.index == 0 || m.substring(g.index - 1, g.index) == " ")) {
                    return true
                }
            }
            return false
        };
        f.prototype.winnow_results = function () {
            var p, r, w, v, l, A, u, y, s, x, q, m, j, h, B, C, o;
            s = new Date();
            this.no_results_clear();
            u = 0;
            y = this.search_field.val() === this.default_text ? "" : d("<div/>").text(d.trim(this.search_field.val())).html();
            l = new RegExp(y.replace(/[-[\]{}()*+?.,\\^$|#\s]/g, "\\$&"), "i");
            m = new RegExp(y.replace(/[-[\]{}()*+?.,\\^$|#\s]/g, "\\$&"), "i");
            o = this.results_data;
            var g, n = [];
            for (j = 0, B = o.length; j < B; j++) {
                r = o[j];
                if (!r.disabled) {
                    if (r.group) {
                        d("#" + r.dom_id).hide();
                        n.push(r.dom_id)
                    } else {
                        if (!(this.is_multiple && r.selected)) {
                            p = false;
                            A = r.dom_id;
                            if ((g = r.keyword.match(l))) {
                                p = true;
                                u += 1;
                                if (g.index == 0 || r.keyword.substring(g.index - 1, g.index) == " " || this.is_best_match(r.keyword, l)) {
                                    n.push(A)
                                }
                            } else {
                                if (r.keyword.indexOf(" ") >= 0 || r.html.indexOf("[") === 0) {
                                    v = r.keyword.replace(/\[|\]/g, "").split(" ");
                                    if (v.length) {
                                        for (h = 0, C = v.length; h < C; h++) {
                                            w = v[h];
                                            if (l.test(w)) {
                                                p = true;
                                                u += 1
                                            }
                                        }
                                    }
                                }
                            } if (p) {
                                if (y.length) {
                                    x = r.html.search(m);
                                    q = r.html.substr(0, x + y.length) + "</em>" + r.html.substr(x + y.length);
                                    q = q.substr(0, x) + "<em>" + q.substr(x)
                                } else {
                                    q = r.html
                                }
                                q = r.icon ? '<img src="' + r.icon + '" class="chosen-icon">' + r.html : r.html;
                                if (d("#" + A).html !== q) {
                                    d("#" + A).html(q)
                                }
                                this.result_activate(d("#" + A));
                                if (r.group_array_index != null) {
                                    d("#" + this.results_data[r.group_array_index].dom_id).show()
                                }
                            } else {
                                if (this.result_highlight && A === this.result_highlight.attr("id")) {
                                    this.result_clear_highlight()
                                }
                                this.result_deactivate(d("#" + A))
                            }
                        }
                    }
                }
            }
            var k, t;
            for (var z = 0; z < this.results_data.length; z++) {
                k = d("#" + this.results_data[z].dom_id);
                t = k.parent();
                k.remove();
                t.append(k)
            }
            if (n.length > 0 && n.length < o.length) {
                n.reverse();
                for (var z = 0; z < n.length; z++) {
                    k = d("#" + n[z]);
                    t = k.parent();
                    k.remove();
                    t.prepend(k)
                }
            }
            if (u < 1 && y.length) {
                return this.no_results(y)
            } else {
                return this.winnow_results_set_highlight()
            }
        };
        f.prototype.winnow_results_clear = function () {
            var g, j, k, i, h;
            this.search_field.val("");
            j = this.search_results.find("li");
            h = [];
            for (k = 0, i = j.length; k < i; k++) {
                g = j[k];
                g = d(g);
                h.push(g.hasClass("group-result") ? g.show() : !this.is_multiple || !g.hasClass("result-selected") ? this.result_activate(g) : void 0)
            }
            return h
        };
        f.prototype.winnow_results_set_highlight = function () {
            var g, h;
            if (!this.result_highlight) {
                h = !this.is_multiple ? this.search_results.find(".result-selected.active-result") : [];
                g = h.length ? h.first() : this.search_results.find(".active-result").first();
                if (g != null) {
                    return this.result_do_highlight(g)
                }
            }
        };
        f.prototype.no_results = function (g) {
            var h;
            h = d('<li class="no-results">' + this.results_none_found + ' "<span></span>"</li>');
            h.find("span").first().html(g);
            return this.search_results.append(h)
        };
        f.prototype.no_results_clear = function () {
            return this.search_results.find(".no-results").remove()
        };
        f.prototype.keydown_arrow = function () {
            var h, g;
            if (!this.result_highlight) {
                h = this.search_results.find("li.active-result").first();
                if (h) {
                    this.result_do_highlight(d(h))
                }
            } else {
                if (this.results_showing) {
                    g = this.result_highlight.nextAll("li.active-result").first();
                    if (g) {
                        this.result_do_highlight(g)
                    }
                }
            } if (!this.results_showing) {
                return this.results_show()
            }
        };
        f.prototype.keyup_arrow = function () {
            var g;
            if (!this.results_showing && !this.is_multiple) {
                return this.results_show()
            } else {
                if (this.result_highlight) {
                    g = this.result_highlight.prevAll("li.active-result");
                    if (g.length) {
                        return this.result_do_highlight(g.first())
                    } else {
                        if (this.choices > 0) {
                            this.results_hide()
                        }
                        return this.result_clear_highlight()
                    }
                }
            }
        };
        f.prototype.keydown_backstroke = function () {
            if (this.pending_backstroke) {
                this.choice_destroy(this.pending_backstroke.find("a").first());
                return this.clear_backstroke()
            } else {
                this.pending_backstroke = this.search_container.siblings("li.search-choice").last();
                return this.pending_backstroke.addClass("search-choice-focus")
            }
        };
        f.prototype.clear_backstroke = function () {
            if (this.pending_backstroke) {
                this.pending_backstroke.removeClass("search-choice-focus")
            }
            return this.pending_backstroke = null
        };
        f.prototype.keypress_checker = function (g) {
			if(g.keyCode == 13) {
				this.enterPressed = true;
				g.preventDefault();
			} else {
				this.enterPressed = false;
			}
		};
        f.prototype.keyup_checker = function (g) {
            var i, h;
            i = (h = g.which) != null ? h : g.keyCode;
            this.search_field_scale();
            switch (i) {
                case 8:
                    if (this.is_multiple && this.backstroke_length < 1 && this.choices > 0) {
                        return this.keydown_backstroke()
                    } else {
                        if (!this.pending_backstroke) {
                            this.result_clear_highlight();
                            return this.results_search()
                        }
                    }
                    break;
                case 13:
                    g.preventDefault();
                    if (this.results_showing && this.enterPressed) {
                        return this.result_select(g)
                    }
                    break;
                case 27:
                    if (this.results_showing) {
                        return this.results_hide()
                    }
                    break;
                case 9:
                case 38:
                case 40:
                case 16:
                case 91:
                case 17:
                    break;
                default:
                    return this.results_search()
            }
        };
        f.prototype.keydown_checker = function (g) {
            var i, h;
            i = (h = g.which) != null ? h : g.keyCode;
            this.search_field_scale();
            if (i !== 8 && this.pending_backstroke) {
                this.clear_backstroke()
            }
            switch (i) {
                case 8:
                    this.backstroke_length = this.search_field.val().length;
                    break;
                case 9:
                    this.mouse_on_container = false;
                    break;
                case 13:
				//  g.preventDefault();
                    break;
                case 38:
                    g.preventDefault();
                    this.keyup_arrow();
                    break;
                case 40:
                    this.keydown_arrow();
                    break
            }
			this.enterPressed = false;
        };
        f.prototype.search_field_scale = function () {
            var p, g, k, i, n, o, m, j, l;
            if (this.is_multiple) {
                k = 0;
                m = 0;
                n = "position:absolute; left: -1000px; top: -1000px; display:none;";
                o = ["font-size", "font-style", "font-weight", "font-family", "line-height", "text-transform", "letter-spacing"];
                for (j = 0, l = o.length; j < l; j++) {
                    i = o[j];
                    n += i + ":" + this.search_field.css(i) + ";"
                }
                g = d("<div />", {
                    style: n
                });
                g.text(this.search_field.val());
                d("body").append(g);
                m = g.width() + 25;
                g.remove();
                if (m > this.f_width - 10) {
                    m = this.f_width - 10
                }
                this.search_field.css({
                    width: m + "px"
                });
                p = this.container.height();
                return this.dropdown.css({
                    top: p + "px"
                })
            }
        };
        f.prototype.generate_field_id = function () {
            var g;
            g = this.generate_random_id();
            this.form_field.id = g;
            return g
        };
        f.prototype.generate_random_id = function () {
            var g;
            g = "sel" + this.generate_random_char() + this.generate_random_char() + this.generate_random_char();
            while (d("#" + g).length > 0) {
                g += this.generate_random_char()
            }
            return g
        };
        f.prototype.generate_random_char = function () {
            var i, h, g;
            i = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXTZ";
            g = Math.floor(Math.random() * i.length);
            return h = i.substring(g, g + 1)
        };
        return f
    })();
    c = function (f) {
        var g;
        return g = f.outerWidth() - f.width()
    };
    a.get_side_border_padding = c
}).call(this);
(function () {
    var a;
    a = (function () {
        function b() {
            this.options_index = 0;
            this.parsed = []
        }
        b.prototype.add_node = function (c) {
            if (c.nodeName === "OPTGROUP") {
                return this.add_group(c)
            } else {
                return this.add_option(c)
            }
        };
        b.prototype.add_group = function (i) {
            var h, e, g, d, f, c;
            h = this.parsed.length;
            this.parsed.push({
                array_index: h,
                group: true,
                label: i.label,
                children: 0,
                disabled: i.disabled
            });
            f = i.childNodes;
            c = [];
            for (g = 0, d = f.length; g < d; g++) {
                e = f[g];
                c.push(this.add_option(e, h, i.disabled))
            }
            return c
        };
        b.prototype.add_option = function (d, e, c) {
            if (d.nodeName === "OPTION") {
                if (d.text !== "") {
                    if (e != null) {
                        this.parsed[e].children += 1
                    }
                    this.parsed.push({
                        array_index: this.parsed.length,
                        options_index: this.options_index,
                        value: d.value,
                        text: d.text,
                        html: d.innerHTML,
                        keyword: jQuery(d).attr("keyword") ? d.innerHTML + " " + jQuery(d).attr("keyword") : d.innerHTML,
                        icon: jQuery(d).attr("icon"),
                        selected: d.selected,
                        disabled: c === true ? c : d.disabled,
                        group_array_index: e,
                        classes: d.className,
                        style: d.style.cssText
                    })
                } else {
                    this.parsed.push({
                        array_index: this.parsed.length,
                        options_index: this.options_index,
                        value: d.value,
                        text: " ",
                        html: "&nbsp;",
                        keyword: "",
                        selected: d.selected,
                        disabled: c === true ? c : d.disabled,
                        group_array_index: e,
                        classes: d.className,
                        style: d.style.cssText,
                        empty: true
                    })
                }
                return this.options_index += 1
            }
        };
        return b
    })();
    a.select_to_array = function (b) {
        var g, f, e, c, d;
        f = new a();
        d = b.childNodes;
        for (e = 0, c = d.length; e < c; e++) {
            g = d[e];
            f.add_node(g)
        }
        return f.parsed
    };
    this.SelectParser = a
}).call(this);
