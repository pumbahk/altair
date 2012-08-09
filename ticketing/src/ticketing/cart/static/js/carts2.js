// new cart flow

var cart = {};

cart.util = {
    datestring_japanize: function(datestring){
        // year, month, day, rest
        var dates = datestring.split(/[ -]/);
        return "%Y年%m月%d日 %time"
            .replace("%Y", dates[0])
            .replace("%m", dates[1])
            .replace("%d", dates[2])
            .replace("%time", dates[3]);
    },

    build_route_path: function (pattern, kwds) {
        return pattern.replace(/\{([^}]+)\}/, function ($0, $1) {
            return kwds[$1] || '';
        });
    },

    render_template: function (template, vars) {
        return template.replace(/\{\{((?:[^}]|\}[^}])*)\}\}/, function (_, n) { return vars[n]; });
    },

    render_template_into: function (jq, template, vars) {
        var regexp = /\{\{((?:[^}]|\}[^}])*)\}\}|((?:[^{]|\{(?:[^{]|$))+)/g, g;
        while ((g = regexp.exec(template))) {
            if (g[1])
                jq.append(vars[g[1]]);
            else if (g[2])
                jq.append(g[2]);
        }
    }
};

cart.events = {
    ON_PERFORMANCE_RESOLVED: "onPerformanceResolved",
    ON_STOCK_TYPE_SELECTED: "onStockTypeSelected",
    ON_CART_CANCELED: "onCartCanceled",
    ON_CART_ORDERED: "onCartOredered",
    ON_VENUE_DATASOURCE_UPDATED: "onVenueDataSourceUpdated"
};
cart.init = function(venues_selection, selected, upper_limit, cart_release_url) {
    cart.app = new cart.ApplicationController();
    cart.app.init(venues_selection, selected, upper_limit, cart_release_url);
};

cart.ApplicationController = function() {
};

cart.ApplicationController.prototype.init = function(venues_selection, selected, upper_limit, cart_release_url) {
    this.performanceSearch = new cart.PerformanceSearch({
        venuesSelection: venues_selection,
        performance: selected[1],
        venue: null
    });
    this.performance = new cart.Performance({
    });
    this.venue = new cart.Venue({
            data_source: null
    });
    // 絞込み
    this.performanceSearchPresenter = new cart.PerformanceSearchPresenter({
        viewType: cart.PerformanceSearchView,
        performanceSearch: this.performanceSearch,
        performance: this.performance
    });
    // 席種
    this.stockTypeListPresenter = new cart.StockTypeListPresenter({
        viewType: cart.StockTypeListView,
        performance: this.performance
    });
    // 会場図
    this.venuePresenter = new cart.VenuePresenter({
        viewType: cart.VenueView,
        performance: this.performance
    });
    // フォーム
    this.orderFormPresenter = new cart.OrderFormPresenter({
        viewType: cart.OrderFormView
    });

    this.performanceSearchPresenter.stockTypeListPresenter = this.stockTypeListPresenter;
    this.stockTypeListPresenter.venuePresenter = this.venuePresenter;
    this.stockTypeListPresenter.orderFormPresenter = this.orderFormPresenter;

    this.performanceSearchPresenter.initialize();
    this.stockTypeListPresenter.initialize();
    this.venuePresenter.initialize();
    this.orderFormPresenter.initialize();

};

cart.PerformanceSearchPresenter = function(params) {
    for (var k in params) {
        this[k] = params[k];
    }
};


cart.PerformanceSearchPresenter.prototype = {
    initialize: function() {
        var self = this;
        this.view = new this.viewType({
            presenter: this,
            el: $("#form1")
        });
        this.view.on(cart.events.ON_PERFORMANCE_RESOLVED,
            function(performance) {self.onPerformanceResolved(performance);});
        this.view.model = this.performanceSearch;
        this.view.render();
    },
    onPerformanceResolved: function(performance_id) {
        // StockTypeList
        var performance = this.performanceSearch.getPerformance(performance_id);
        this.performance.url = performance.seat_types_url;
        this.performance.fetch();
    }
};
_.extend(cart.PerformanceSearchPresenter.prototype, Backbone.Event);

cart.StockTypeListPresenter = function(params) {
    for (var k in params) {
        this[k] = params[k];
    }
};

cart.StockTypeListPresenter.prototype = {
    initialize: function() {
        var self = this;
        this.view = new this.viewType({
        });
        this.performance.on("change",
            function() {self.onPerformanceChanged();});
        this.view.on(cart.events.ON_STOCK_TYPE_SELECTED,
            function(products_url) {self.onStockTypeSelected(products_url);});
    },
    onPerformanceChanged: function() {
        var stockTypes = this.performance.get("seat_types");
        // collectionを作ってViewにpush
        var stockTypeCollection = new Backbone.Collection();
        for (var i=0; i < stockTypes.length; i++) {
            var stockType = new cart.StockType(stockTypes[i]);
            stockTypeCollection.push(stockType);
        }
        this.view.collection = stockTypeCollection;
        this.view.render();
    },
    onStockTypeSelected: function(products_url) {
        var self = this;
        self.orderFormPresenter.hideOrderForm();
        $.getJSON(
            products_url,
            function(data) {
                var products = data.products;
                var productCollection = new cart.ProductQuantityCollection();
                for (var i=0; i < products.length; i++) {
                    var product = products[i];
                    var p = new cart.ProductQuantity(product);
                    productCollection.push(p);
                }
                var selected = self.view.selected;
                self.orderFormPresenter.showOrderForm(selected, productCollection);
            }
        );
    }
};

_.extend(cart.StockTypeListPresenter.prototype, Backbone.Event);


cart.VenuePresenter = function(params) {
    for (var k in params) {
        this[k] = params[k];
    }
};

cart.VenuePresenter.prototype = {
    defaults: {
        viewType: null,
    },
    initialize: function() {
        var self = this;
        this.callbacks = {
            click: this.click,
            selectable: this.selectable,
            select: this.select
        };
        this.view = new this.viewType({
            presenter: this
        });
        this.performance.on("change",
            function() {self.onPerformanceChanged();});
    },
    onPerformanceChanged: function() {
        var dataSource = this.performance.createDataSource();
        this.view.updateVenueViewer(dataSource, this.callbacks);
    },
    selectable: function (viewer, seat) {
        return true;
        // 席が選択可能か返す
        // if (currentStockTypeId == "") {
        //     return true;
        // }
        var selectedStockType = this.seatTypes.selectedStockType;

        var isValidStockType = (seat.meta.stock_type_id == selectedStockType.id);
        var isVacant = (seat.meta.status == 1);
        return isValidStockType && isVacant && seat.meta.is_hold;
    },

    click: function (viewer, seat, highlighted) {
        // クリック位置から、座席選択をする
        // $.each(highlighted, function (id, seat) {
        //     if (seat.selected()) {
        //         seat.selected(false);
        //     } else {
        //         var selectable = viewer.selectionCount < get_current_quantity();
        //         seat.selected(selectable);
        //     }
        // });
    },
    
    select: function (viewer, selection) {
        // 選択された後のコールバック
        $.each(selection, function (i, seat) {
            console.log(seat);
        });
    },
};
_.extend(cart.VenuePresenter.prototype, Backbone.Event);


cart.PerformanceSearchView = Backbone.View.extend({
    initialize: function() {
        var self = this;
        this.selection = this.$el.find("#date-select");
        this.selection.on("change",
            function() {self.onDateSelectionChanged()});
        this.venueSelection = this.$el.find("#venue-select");
        this.venueSelection.on("change",
            function() {self.onVenueSelectionChanged()});
    },
    render: function() {
        // 絞り込み条件を設定する
        var selected = this.model.get("performance");    
        var venues = this.model.getVenues(selected);
        var venueSelection = this.$el.find("#venue-select");
        venueSelection.empty();
        for (var i=0; i < venues.length; i++) {
            var venue = venues[i];
            var opt = $('<option/>');
            $(opt).attr('value', venue.id);
            $(opt).text(venue.name);
            $(venueSelection).append(opt);
        }
        $(venueSelection).change();
    },
    onDateSelectionChanged: function() {
        var performance = $(this.selection).val();
        this.model.set("performance", 
            performance);
        this.render();
    },
    onVenueSelectionChanged: function() {
        this.trigger(cart.events.ON_PERFORMANCE_RESOLVED,
            $(this.venueSelection).val());
    }
});

cart.PerformanceSearch = Backbone.Model.extend({
    defaults: {
        venuesSelection: null,
        performance: null
    },
    getVenues: function(selected) {
        var venuesSelection = this.get('venuesSelection');
        return venuesSelection[selected];
    },
    getPerformance: function(id) {
        var venues = this.getVenues(this.get("performance"));
        for (var i=0; i < venues.length; i++) {
            var venue = venues[i];
            if (venue.id == id) {
                return venue;
            }
        }
    },
});

cart.Performance = Backbone.Model.extend({
    createDataSource: function() {
        return createDataSource(this.attributes);
    }
});

cart.StockType = Backbone.Model.extend({
});


cart.StockTypeListView = Backbone.View.extend({
    defaults: {
        arrow: null,
        selected: null,
        el: $('#selectSeatType')
    },

    render: function() {
        var self = this;
        var ul = $('#seatTypeList');
        ul.empty();

        this.collection.each(function(stockType) {
            var item = $('<li></li>')
               .append(
                 $('<input type="radio" name="seat_type" />')
                 .attr('value', stockType.get("products_url")))
               .append(
                 $('<span class="seatColor"></span>')
                 .css('background-color', stockType.get("style").fill.color))
               .append(
                 $('<span class="seatName"></span>')
                 .text(stockType.get("name")))
               .append(
                 $('<span class="seatStatus"></span>'))
              .appendTo(ul);
            item.data(stockType);
            });
        ul.find("li:even").addClass("seatEven");
        ul.find("li:odd").addClass("seatOdd");
        this.updateArrowPos();
    },

    updateArrowPos: function updateArrowPos() {
        if (this.arrow) {
            var ul = $('#seatTypeList');
            var scrollY = ul.parent().scrollTop();
            this.arrow.css({
                right: "0px",
                top: this.arrowAbsPos - scrollY + "px"
            });
        }
    },
    initialize: function() {
        this.selected = null;
        this.arrow = $('<div></div>');
        this.arrow.addClass("arrow")
        this.$el.append(this.arrow);
        var ul = $('#seatTypeList');
        //var ulTopOffset = ul.parent()[0].offsetTop;
        //ul.parent().scroll(updateArrowPos);
        var self = this;
        ul.delegate('li', 'click', function () {
          self.select($(this));
        });
        this.form = $('#order-form');
        this.form.hide();
    },

    reset: function() {
        if (this.selected) {
            this.selected.removeClass('selected');
            var radio = this.selected.find(':radio');
            if (radio.length) {
              radio[0].checked = false;
              radio.change();
            }
        }

        if (this.arrow) {
          this.arrow.remove();
        }

        this.selected = this.arrow = null;
        return;
    },

    select: function (stock_type_item) {
        var it = stock_type_item;
        if (!it.hasClass('selected')) {
            if (this.selected) {
                this.selected.removeClass('selected');
                this.selected.css('margin-bottom', 0);
            }
            it.addClass('selected');
            this.selected = it;
            //arrowAbsPos = it[0].offsetTop + ulTopOffset;
            //updateArrowPos();
        }
        var radio = it.find(':radio');
        if (radio.length) {
            radio[0].checked = true;
            radio.change();
            var formContainer = it.find('.formContainer');
            this.trigger(cart.events.ON_STOCK_TYPE_SELECTED, 
                $(radio).val());

        }
    
            
    },
});

cart.OrderFormPresenter = function(params) {
    for (var k in params) {
        this[k] = params[k];
    }
};

cart.OrderFormPresenter.prototype = {
    initialize: function() {
        this.view = new this.viewType({
            el: $('#order-form'),
            presenter: this
        });
    },
    hideOrderForm: function() {
        this.view.hideForm();
    },
    showOrderForm: function(selected_stock_type_el, products) {
        this.view.selected_stock_type_el = selected_stock_type_el;
        this.view.collection = products;
        this.view.render();
    }
};

_.extend(cart.OrderFormPresenter.prototype, Backbone.Event);

cart.OrderFormView = Backbone.View.extend({
    defaults: {
        el: $('#order-form'),
        selected_stock_type_el: null
    },
    initialize: function() {
        this.$el.hide();
        this.presenter = this.options.presenter;
    },
    hideForm: function() {
        this.$el.hide();
    },
    render: function() {
        var self = this;
        if (!this.selected_stock_type_el) {
            this.$el.hide();
            return;
        }
        var stockType = this.selected_stock_type_el.data();
        var selected = this.selected_stock_type_el;
        this.$el.css('position', 'absolute');
        var top = $(selected).position().top;
        var height = $(selected).height();
        this.$el.css('top', top + height);
        $('#selected-seats').empty();
        $('#payment-seat-products').empty();
        
        this.collection.each(function(product) {
            self.addProduct(product);
        });
        $(selected).css('margin-bottom', this.$el.height());
        if (stockType.get("quantity_only")) {
            $('#btn-select-buy-container').hide();
            $('#btn-entrust-buy-container').hide();
            $('#btn-buy-container').show();
        } else {
            $('#btn-select-buy-container').show();
            $('#btn-entrust-buy-container').show();
            $('#btn-buy-container').hide();
        }
        this.$el.show();
    },
    addProduct: function(product) {
        var name = $('<span class="productName"></span>');
        name.text(product.get("name"));
        var payment = $('<span class="productPrice"></span>');
        payment.text('￥' + product.get("price"));
        var quantity = $('<span class="productQuantity">');
        var pullDown = $('<select />').attr('name', "product-" + product.id);
        for (var i = 0; i < upper_limit+1; i++) {
            $('<option></option>').text(i).val(i).appendTo(pullDown);
        }
        cart.util.render_template_into(quantity, product.get("unit_template"), { num: pullDown });
        $('<li class="productListItem"></li>')
            .append(name)
            .append(payment)
            .append(quantity)
            .appendTo($('#payment-seat-products'));
        
    }
});


cart.Product = Backbone.Model.extend({
    defaults: {
        quantity_power: 1,
        id: null,
        name: null,
        price: '0', // 表示用
        unit_template: null
    },
    initialize: function() {
        
    }
});

cart.ProductQuantity = Backbone.Model.extend({

});

cart.ProductQuantityCollection = Backbone.Collection.extend({
    defaults: {
        stockType: null
    },
    model: cart.ProductQuantity,
    initialize: function() {
    },

    setStockType: function(stockType) {
        this.url = stockType.productsUrl;
        this.fetch({success: function() {this.change();}});
    }
});

cart.VenueView = Backbone.View.extend({
    initialize: function() {
        // VenueViewer作成
        this.currentViewer = $('.venueViewer');
        this.presenter = this.options.presenter;
        this.readOnly = true;
    }, 
    updateVenueViewer: function(dataSource, callbacks) {
        this.currentViewer.venueviewer({
            dataSource: dataSource,
            callbacks: callbacks
        })
        this.currentViewer.venueviewer("load");
        this.render();
    },
    render: function() {
        if (this.readOnly) {
            this.currentViewer.venueviewer("uimode", "move");
        } else {
            this.currentViewer.venueviewer("uimode", "select");
        }
        this.currentViewer.venueviewer("refresh");
    }
});


cart.Venue = Backbone.Model.extend({
    updateDataSource: function(params) {
        var factory = newMetadataLoaderFactory(params.data_source.seats);
        var dataSource = {
          drawing: function (next, error) {
            $.ajax({
              url: params.data_source.venue_drawing,
              dataType: 'xml',
              success: function (data) { next(data); },
              error: function (xhr, text) {
                error("Failed to load drawing data (" + text + ")");
              }
            });
          },
          stockTypes: function (next, error) {
            var stock_types = {};
            for (var i = params.seat_types.length; --i >= 0;)
              stock_types[params.seat_types[i].id] = params.seat_types[i];
            next(stock_types);
          },
          info: factory(function (data) { return data['info']; }),
          seats: factory(function (data) { return data['seats']; }),
          areas: factory(function (data) { return data['areas']; }),
          seat_adjacencies: function (next, error, length) {
            var _params = $.extend(params, { length_or_range: length });
            $.ajax({
              url: util.build_route_path(params.data_source.seat_adjacencies._params),
              dataType: 'json',
              success: function (data) { next(data); },
              error: function (xhr, text) {
                error("Failed to load adjacency data (" + text + ")");
              }
            });
          },
          stock_types: function (next, error) {
            continuations.stock_types_loaded.continuation(next, error);
          }
        };
        this.set('dataSource', dataSource);
        this.trigger(cart.events.ON_VENUE_DATASOURCE_UPDATED);
    },
    defaults: {
    },
    initialize: function() {
    },

});


function newMetadataLoaderFactory(url) {
  var conts = [], allData = null, first = true;
  return function createMetadataLoader(fetch) {
    return function metadataLoader(next, error) {
      conts.push({ fetch: fetch, next: next, error: error });
      if (first) {
        $.ajax({
          url: url,
          dataType: 'json',
          success: function(data) {
            allData = data;
            var _conts = conts;
            conts = [];
            for (var i = 0; i < _conts.length; i++)
              _conts[i].next(_conts[i].fetch(data));
          },
          error: function(xhr, text) {
            var message = "Failed to load " + key + " (reason: " + text + ")";
            var _conts = conts;
            conts = [];
            for (var i = 0; i < _conts.length; i++)
              _conts[i].error(message);
          }
        });
        first = false;
        return;
      } else {
        if (allData)
          next(fetch(allData));
      }
    };
  };
}

function createDataSource(params) {
  var factory = newMetadataLoaderFactory(params.data_source.seats);
  return {
    drawing: function (next, error) {
      $.ajax({
        url: params.data_source.venue_drawing,
        dataType: 'xml',
        success: function (data) { next(data); },
        error: function (xhr, text) {
          error("Failed to load drawing data (" + text + ")");
        }
      });
    },
    stockTypes: function (next, error) {
      var stock_types = {};
      for (var i = params.seat_types.length; --i >= 0;)
        stock_types[params.seat_types[i].id] = params.seat_types[i];
      next(stock_types);
    },
    info: factory(function (data) { return data['info']; }),
    seats: factory(function (data) { return data['seats']; }),
    areas: factory(function (data) { return data['areas']; }),
    seat_adjacencies: function (next, error, length) {
      var _params = $.extend(params, { length_or_range: length });
      $.ajax({
        url: util.build_route_path(params.data_source.seat_adjacencies._params),
        dataType: 'json',
        success: function (data) { next(data); },
        error: function (xhr, text) {
          error("Failed to load adjacency data (" + text + ")");
        }
      });
    },
    stock_types: function (next, error) {
      continuations.stock_types_loaded.continuation(next, error);
    }
  };
}

