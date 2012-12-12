describe("Combobox ui ",  function(){
    var utils = {
        makeDummyFetchApi: function(seq){
            return function(){
                var data = {status: true, data: seq};
                return $.Deferred().resolve(data);
            }
        }
    };
    describe("initialization is success", function(){
        var models;
        beforeEach(function(){
            models = {
                organization:  new combobox.ComboboxSelection({targetObject: "organization"}),
                event:  new combobox.ComboboxSelection({targetObject: "event"}),
                performance:  new combobox.ComboboxSelection({targetObject: "performance" }),
                product:  new combobox.ComboboxSelection({targetObject: "product"})
            };
        });

        describe("model logic only", function(){
            it("after last combo selection is selected, then, call back is called", function(){
                var finishResult = null;            
                var gateway = new combobox.ForTicketPreviewComboboxGateway({
                    models:models, 
                    apis: {}, 
                    finishCallback: function(r){finishResult = r;}
                });
                models.product.selectValue({name: "foo", pk: 1});
                
                expect(finishResult).toNotBe(null);
                expect(finishResult["product"]).toEqual({name: "foo", pk: 1});
            });
            it("last 2 combo chain... if prev selection is selected after that,  chained selection's candidats are fetched", function(){
                var finishResult = null;            
                var product_list_candidates = [{"name": "foo", "pk": 1}, {"name": "bar", "pk": 2}];            

                var gateway = new combobox.ForTicketPreviewComboboxGateway({
                    models:models, 
                    apis: {
                        product_list: utils.makeDummyFetchApi(product_list_candidates)
                    }, 
                    finishCallback: function(r){finishResult = r;}
                });

                // chain : performance -> product
                expect(models.performance.get("result")).toEqual(null);
                expect(models.product.get("candidates")).toEqual([]);
                models.performance.selectValue({name: "foo", pk: 1});
                expect(models.performance.get("result")).toNotEqual(null);            
                expect(models.product.get("candidates")).toEqual(product_list_candidates);

                expect(finishResult).toBeNull();
            });
        });
        describe("include view", function(){
            var createViewModel =function(ks){
                var o = {};
                _(ks).each(function(k){o[k] = jasmine.createSpy(k)});
                return o;
            };

            describe("last 2 combo chain...", function(){
                var view_models;
                var finishResult = null;
                beforeEach(function(){
                    view_models = {
                        performance: createViewModel(["refresh", "draw", "onSelect"]), 
                        product: createViewModel(["refresh", "draw", "onSelect"])
                    };
                    views = {
                        performance:  new combobox.ComboboxView({vms: {input: view_models.performance}, model: models.performance}), 
                        product:  new combobox.ComboboxView({vms: {input: view_models.product}, model: models.product})
                    };
                });
                it("chained view calll draw()", function(){
                    // chain: performance -> product
                    var product_candidats = [{name: "foo", pk: 1}, {name: "bar", pk: 2}];
                    var apis = {
                        product_list: utils.makeDummyFetchApi(product_candidats)
                    };
                    
                    var gateway = new combobox.ForTicketPreviewComboboxGateway({
                        models:models, apis: apis, 
                        finishCallback: function(r){finishResult = r;}
                    });

                    expect(view_models.product.draw.callCount).toEqual(0);
                    models.performance.selectValue({name: "performance", pk: 100});
                    expect(view_models.product.draw.callCount).toEqual(1);

                    expect(view_models.product.onSelect.callCount).toEqual(0);
                });
                it("chained view calll draw() and if a length of fetched candidates is 1, then, auto select it.", function(){
                    // chain: performance -> product
                    var product_candidats = [{name: "foo", pk: 1}];
                    var apis = {
                        product_list: utils.makeDummyFetchApi(product_candidats)
                    };
                    
                    var gateway = new combobox.ForTicketPreviewComboboxGateway({
                        models:models, apis: apis, 
                        finishCallback: function(r){finishResult = r;}
                    });

                    models.performance.selectValue({name: "performance", pk: 100});
                    expect(view_models.product.onSelect.callCount).toEqual(1);
                });
            });
            it("semi integration... organization -> event -> performance -> product", function(){
                var createViewModel =function(ks){
                    var o = {};
                    _(ks).each(function(k){o[k] = jasmine.createSpy(k)});
                    o.onSelect = function(){this.model.get("")}
                    return o;
                };

                var view_models = {
                    organization: {
                        refresh: jasmine.createSpy(""), 
                        draw: jasmine.createSpy(""),
                        onSelect: function(){ models.organization.selectValue(models.organization.get("candidates")[0])}
                    }, 
                    event: {
                        refresh: jasmine.createSpy(""), 
                        draw: jasmine.createSpy(""),
                        onSelect: function(){ models.event.selectValue(models.event.get("candidates")[0])}
                    }, 
                    performance: {
                        refresh: jasmine.createSpy(""), 
                        draw: jasmine.createSpy(""),
                        onSelect: function(){ models.performance.selectValue(models.performance.get("candidates")[0])}
                    }, 
                    product: {
                        refresh: jasmine.createSpy(""), 
                        draw: jasmine.createSpy(""),
                        onSelect: function(){ models.product.selectValue(models.product.get("candidates")[0])}
                    }
                };
                var views = {
                    organization:  new combobox.ComboboxView({vms: {input: view_models.organization}, model: models.organization}), 
                    event:  new combobox.ComboboxView({vms: {input: view_models.event}, model: models.event}), 
                    performance:  new combobox.ComboboxView({vms: {input: view_models.performance}, model: models.performance}), 
                    product:  new combobox.ComboboxView({vms: {input: view_models.product}, model: models.product})
                };

                var apis = {
                    organization_list: utils.makeDummyFetchApi([{name: "organization:1", pk: 1}]), 
                    event_list: utils.makeDummyFetchApi([{name: "event:1", pk: 1}, {name: "event:2", pk: 2}]), 
                    performance_list: utils.makeDummyFetchApi([{name: "performance:1", pk: 1}, {name: "performance:2", pk: 2}]), 
                    product_list: utils.makeDummyFetchApi([{name: "product:1", pk: 1}, {name: "product:2", pk: 2}])
                };

                var gateway = new combobox.ForTicketPreviewComboboxGateway({
                    models:models, apis: apis, 
                    finishCallback: function(r){finishResult = r;}
                });

                // it("first initialization", function(){
                expect(models.organization.get("candidates")).toEqual([]);
                expect(models.event.get("candidates")).toEqual([]);
                expect(models.performance.get("candidates")).toEqual([]);
                expect(models.product.get("candidates")).toEqual([]);
                // });

                // it("organization candidats are fetched (event candidats are auto fetched)", function(){
                gateway.organization.updateCandidates();

                expect(models.organization.get("candidates")).toNotEqual([]);
                expect(models.event.get("candidates")).toNotEqual([]); // auto select
                expect(models.performance.get("candidates")).toEqual([]);
                expect(models.product.get("candidates")).toEqual([]);

                expect(models.organization.get("result")).toEqual({name: "organization:1", "pk": 1});
                // });

                // it("event is selected", function(){
                models.event.selectValue({name: "event:2", pk:2});

                expect(models.organization.get("candidates")).toNotEqual([]);
                expect(models.event.get("candidates")).toNotEqual([]); 
                expect(models.performance.get("candidates")).toNotEqual([]);
                expect(models.product.get("candidates")).toEqual([]);

                expect(models.event.get("result")).toEqual({name: "event:2", "pk": 2});
                // });

                // it("performance is selected", function(){
                models.performance.selectValue({name: "performance:2", pk:2});

                expect(models.organization.get("candidates")).toNotEqual([]);
                expect(models.event.get("candidates")).toNotEqual([]); 
                expect(models.performance.get("candidates")).toNotEqual([]);
                expect(models.product.get("candidates")).toNotEqual([]);

                expect(models.performance.get("result")).toEqual({name: "performance:2", "pk": 2});
                // });

                // it("product is selected", function(){
                models.product.selectValue({name: "product:2", pk:2});
                expect(finishResult).toEqual({
                    organization: {name: "organization:1", pk: 1}, 
                    event: {name: "event:2", pk: 2}, 
                    performance: {name: "performance:2", pk: 2}, 
                    product: {name: "product:2", pk: 2}, 
                })
                // })

                /// event selection is reselect
                models.event.selectValue({name: "event:2", pk:2});

                expect(models.organization.get("candidates")).toNotEqual([]);
                expect(models.event.get("candidates")).toNotEqual([]); 
                expect(models.performance.get("candidates")).toNotEqual([]); // fetch new candidates
                expect(models.product.get("candidates")).toEqual([]);

                expect(models.event.get("result")).toEqual({name: "event:2", "pk": 2});
                expect(models.performance.get("result")).toEqual({name: "performance:1", "pk": 1}); // first selection is set(default)
                expect(models.product.get("result")).toBeNull();

            });
        });
    });
});
