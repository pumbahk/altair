describe("ticket preview ui",  function(){
    var utils = {
        makeDummyFetchApi: function(data){
            return function(){
                var data = {status: true, data: data};
                return $.Deferred().resolve(data).promise();
            }
        }
    };

    describe("around resize", function(){
        var finished;
        var gateway;
        var models;
        beforeEach(function(){
            models = {
                svg: new preview.SVGStore(),
                preview: new preview.PreviewImageStore(),
                vars: new preview.TemplateVarStore(), 
                params: new preview.ParameterStore({ticket_format: {pk: 1}})
            };

            finished = {
                normalize: false, 
                previewbase64: false, 
                collectvars: false
            };

            gateway = new preview.ApiCommunicationGateway({
                models:models, 
                message:core.ConsoleMessage, 
                apis: {
                    normalize: function(params){
                        finished.normalize = true;
                        return $.Deferred().resolve({data: "normalize-svg", status:true}).promise();
                    }, 
                    previewbase64: function(params){
                        finished.previewbase64 = true;
                        return $.Deferred().resolve({data: "+svg-data+", width: "300px", height: "200px", status:true }).promise();
                    }, 
                    collectvars: function(params){
                        finished.collectvars = true;
                        return $.Deferred().resolve({data: ["foo", "bar", "event", "performance"], status:true }).promise();
                    }
                }
            });
            models.preview.resizeImage = jasmine.createSpy("");
            gateway.svgRawToX();            
        });
        it("initial fetch iamge", function(){
            // raw -> normalize
            expect(models.params.get("default_sx")).toEqual(2.0);
            expect(models.params.get("default_sy")).toEqual(2.0);
            expect(models.svg.get("normalize")).toEqual("normalize-svg")
            expect(finished.normalize).toBe(true);

            // normalize -> image
            expect(models.preview.get("data")).toEqual("data:image/png;base64,+svg-data+");
            expect(models.preview.get("width")).toEqual("300px");
            expect(models.preview.get("height")).toEqual("200px");
            expect(finished.previewbase64).toBe(true);

            expect(models.preview.get("rendering_width")).toEqual("300px");
            expect(models.preview.get("rendering_height")).toEqual("200px");
        });
        describe ("after initial fetch image ... access template vars", function(){
            it("", function(){
                // normalize -> template vars
                expect(finished.collectvars).toBe(true);
                expect(models.vars.get("changed")).toBe(false);
                models.vars.get("vars").models[0].set("value", 100);
                expect(models.vars.get("changed")).toBe(true);
            })
        });
        describe ("after initial fetch image .... access around image", function(){
            var finished; 
            var gateway2;
            beforeEach(function(){
                finished = {
                    previewbase64: false
                };
                gateway2 = new preview.ApiCommunicationGateway({
                    models:models, 
                    message:core.ConsoleMessage, 
                    apis: {
                        previewbase64: function(params){
                            finished.previewbase64 = true;
                            return $.Deferred().resolve({data: "+svg-data+", width: "300px", height: "200px", status:true }).promise();
                        }
                    }
                });
            });
            it("scale image (default_sx >= sx), resize only", function(){
                models.preview.resizeImage = jasmine.createSpy("");
                models.params.set("sx", 1.2);
                models.params.set("sy", 1.4);

                expect(finished.previewbase64).toBe(false);
                gateway2.svgFilledToX();

                expect(finished.previewbase64).toBe(false);
                expect(models.preview.resizeImage.argsForCall).toEqual([["360px", "280px"]]);
                expect(models.params.get("default_sx", 2.0));
                expect(models.params.get("default_sy", 2.0));
            });
            describe("scale image (default_sx < sx) .. fetch image and resize", function(){
                it("fetch image and resize", function(){
                    models.preview.initialImage = jasmine.createSpy("");
                    models.params.set("sx", 3.0);
                    models.params.set("sy", 1.4);

                    expect(finished.previewbase64).toBe(false);
                    gateway2.svgFilledToX();

                    expect(finished.previewbase64).toBe(true);
                    expect(models.preview.initialImage.argsForCall).toEqual([["300px", "200px", "900px", "280px"]]);
                    expect(models.params.get("default_sx", 3.0)); //max(sx, sy)
                    expect(models.params.get("default_sy", 3.0));
                });
                it("fetch image and resize, and refetch another image", function(){
                    // resize and fetch image
                    models.params.set("sx", 3.0);
                    gateway2.svgFilledToX();
                    expect(models.params.get("default_sx", 3.0)); //max(sx, sy)

                    /// fetch another image (with D&D)

                    finished = {
                        normalize: false, 
                        previewbase64: false
                    };

                    gateway = new preview.ApiCommunicationGateway({
                        models:models, 
                        message:core.ConsoleMessage, 
                        apis: {
                            normalize: function(params){
                                finished.normalize = true;
                                return $.Deferred().resolve({data: "second:normalize-svg", status:true}).promise();
                            }, 
                            previewbase64: function(params){
                                finished.previewbase64 = true;
                                return $.Deferred().resolve({data: "+second:svg-data+", width: "200px", height: "500px", status:true }).promise();
                            }
                        }
                    });
                    gateway.svgRawToX();            

                    // raw -> normalize
                    expect(models.params.get("default_sx")).toEqual(2.0);
                    expect(models.params.get("default_sy")).toEqual(2.0);
                    expect(models.svg.get("normalize")).toEqual("second:normalize-svg")
                    expect(finished.normalize).toBe(true);

                    // normalize -> image
                    expect(models.preview.get("data")).toEqual("data:image/png;base64,+second:svg-data+");
                    expect(models.preview.get("width")).toEqual("200px");
                    expect(models.preview.get("height")).toEqual("500px");
                    expect(finished.previewbase64).toBe(true);
                });
            });
        });
    });
});