describe("QRApp (order: add ticket => print ticket)",  function(){
  var DummyMessageView = {error: console.log.bind(console), 
                          info: console.log.bind(console)};

  it("call datastore.clearnBuffer() if clear qrcode input button", function(){
    var dataStore = new DataStore();
    var inputView = new QRInputView({datastore: dataStore});
    dataStore.cleanBuffer = jasmine.createSpy("");
    var service = {}
    var appletView = new AppletView({service: service,  datastore: dataStore, appviews: {messageView: DummyMessageView}});

    expect(dataStore.cleanBuffer.callCount).toEqual(0);
    inputView.clearQRCodeInput();
    expect(dataStore.cleanBuffer.callCount).toEqual(1);
  });

  describe("print unit have 2kind states.",  function(){
    var dataStore;
    beforeEach(function(){
      dataStore = new DataStore();
    });

    var _callFUT = function(){
      return dataStore.setPrintStrategy.apply(dataStore, arguments);
    };
    it("datastore print unit receive 'order' then",  function(){
      _callFUT("order");
      expect(dataStore.get("print_unit")).toEqual("order")
      expect(dataStore.get("print_strategy")).toEqual("同一注文の券面まとめて発券")

    });
    it("datastore print unit receive 'token' then",  function(){
      _callFUT("anything.other.input");
      expect(dataStore.get("print_unit")).toEqual("token")
      expect(dataStore.get("print_strategy")).toEqual("個別に発券")
    });
  });

  describe("add ticket phase(AppletView)",  function(){
    var dataStore;
    var service;
    var appletView;

    beforeEach(function(){
      dataStore = new DataStore();        
      service = {
        createTicketFromJSObject: jasmine.createSpy(""), 
        addTicket: jasmine.createSpy("")
      };
    });

    function _makeOne(opts){
      return new AppletView(opts);
    };

    describe("add ticket",  function(){
      it("datastore.print_unit is token then add ticket delegating applet method", function(){
        dataStore.setPrintStrategy("token");
        
          var target = _makeOne({service: service,  datastore: dataStore, appviews: {messageView: {error: console.log, info:console.log}}});
        var ticket = {ticket_template_id: 1}
        target._addTicket(ticket);

        expect(service.createTicketFromJSObject.callCount).toEqual(1);
        expect(service.createTicketFromJSObject.mostRecentCall.args[0]).toEqual(ticket);
        expect(service.addTicket.callCount).toEqual(1);

        expect(dataStore.get("print_num")).toEqual(1);
      });

      it("datastore.print_unit is order then using buffer", function(){
        dataStore.set("ticket_buffers", {addTicket: jasmine.createSpy("")});

        dataStore.setPrintStrategy("order");

          var target = _makeOne({service: service,  datastore: dataStore, appviews: {messageView: {error: console.log, info:console.log}}});
        var ticket = {ticket_template_id: 1}
        target._addTicket(ticket);

        expect(service.createTicketFromJSObject.callCount).toEqual(0); // not called
        expect(dataStore.get("ticket_buffers").addTicket.callCount).toEqual(1)
        expect(dataStore.get("ticket_buffers").addTicket.mostRecentCall.args[0]).toEqual(ticket)

        expect(dataStore.get("print_num")).toEqual(1);
      });
      it("datastore.print_unit is order print_num is exactly, total number of added tickets", function(){
        dataStore.set("ticket_buffers", {addTicket: jasmine.createSpy("")});

        dataStore.setPrintStrategy("order");

          var target = _makeOne({service: service,  datastore: dataStore, appviews: {messageView: {error: console.log, info:console.log}}});

        var ticket0 =  {ticket_template_id: 1};
        var ticket1 =  {ticket_template_id: 1};
        var ticket2 =  {ticket_template_id: 2};
        target._addTicket(ticket0);
        target._addTicket(ticket1);
        target._addTicket(ticket2);

        expect(dataStore.get("print_num")).toEqual(3);
      });
      describe("datastore.tickets buffer", function(){
        var _makeOne = function(){
          return TicketBuffer();
        };

        it("add tickets, then buffers has added ticket", function(){
          target = _makeOne()
          expect(target.buffers[1]).toBeUndefined();

          var ticket =  {ticket_template_id: 1,  ticket_template_name: "FooParty(自由)"};
          target.addTicket(ticket);

          expect(target.buffers[ticket.ticket_template_id]).toEqual([ticket]);
        });
        it("add tickets, multiple, then classified", function(){
          var target = _makeOne()
          expect(target.buffers[1]).toBeUndefined();

          var ticket0 =  {ticket_template_id: 1,  ticket_template_name: "FooParty(自由)"};
          var ticket1 =  {ticket_template_id: 1,  ticket_template_name: "FooParty(自由)"};
          var ticket2 =  {ticket_template_id: 2,  ticket_template_name: "FooParty(指定)"};
          target.addTicket(ticket0);
          target.addTicket(ticket1);
          target.addTicket(ticket2);

          expect(target.buffers[1]).toEqual([ticket0, ticket1]);
          expect(target.buffers[2]).toEqual([ticket2]);
        });
      });
    });
  });

  describe("print ticket", function(){
    var dataStore;
    var service;
    var appletView;

    beforeEach(function(){
      dataStore = new DataStore();        
      service = {
      };
    });

    function _makeOne(opts){
      return new AppletView(opts);
    };
    it("if print unit is token, then,  call applet printAll, directly", function(){
      service.printAll = jasmine.createSpy("")
      var target = _makeOne({service: service,  datastore: dataStore, appviews: {messageView: DummyMessageView}});
      dataStore.set("printed", true);
      dataStore.setPrintStrategy("token");

      spyOn(target, "_printAllWithBuffer");
      spyOn(target, "_afterPrintAll");

      target.sendPrintSignalIfNeed();

      expect(target._printAllWithBuffer.callCount).toEqual(0);
      expect(service.printAll.callCount).toEqual(1)
      expect(target._afterPrintAll.callCount).toEqual(1);
    });

    describe("print unit is order", function(){
      beforeEach(function(){
        dataStore.set("printed", true);
        dataStore.setPrintStrategy("order");
        dataStore.get("ticket_buffers").clean();
      });

      it("if print unit is order, then,  call printWithBuffer", function(){
        var target = _makeOne({service: service,  datastore: dataStore, appviews: {messageView: DummyMessageView}});
        spyOn(target, "_printAllWithBuffer");
        spyOn(target, "_afterPrintAll");

        target.sendPrintSignalIfNeed();

        expect(target._printAllWithBuffer.callCount).toEqual(1);
        expect(target._afterPrintAll.callCount).toEqual(1);
      })

      describe("when, call _printAllWithBuffer", function(){
        beforeEach(function(){
          service = {
            createTicketFromJSObject: jasmine.createSpy(""), 
            addTicket: jasmine.createSpy("")
          };
        });

        it("after then, ticket_template_id is set.", function(){
          service.printAll = jasmine.createSpy("");
          var ticket = {ticket_template_id: 1, ticket_template_name: "FooParty(自由)"};
          dataStore.get("ticket_buffers").addTicket(ticket);
          

          var target = _makeOne({service: service,  datastore: dataStore, appviews: {messageView: DummyMessageView}});
          dataStore.unbind("change:ticket_template_id");

          expect(dataStore.get("ticket_template_id")).toBeNull();
          target._printAllWithBuffer();
          expect(dataStore.get("ticket_template_id")).toEqual(1);
        });

        it("after then, All buffered ticket is consumed", function(){
          service.printAll = jasmine.createSpy("");
          var ticket = {ticket_template_id: 1, ticket_template_name: "FooParty(自由)"};
          dataStore.get("ticket_buffers").addTicket(ticket);

          var target = _makeOne({service: service,  datastore: dataStore, appviews: {messageView: DummyMessageView}});
          dataStore.unbind("change:ticket_template_id");
          
          expect(dataStore.get("print_num", 1));
          target._printAllWithBuffer();
          expect(service.printAll.callCount).toEqual(1);
          expect(dataStore.get("print_num", 0));
        });

        it("after then, All buffered ticket is consumed, multiple tickets", function(){
          service.printAll = jasmine.createSpy("");
          var ticket0 =  {ticket_template_id: 1,  ticket_template_name: "FooParty(自由)"};
          var ticket1 =  {ticket_template_id: 1,  ticket_template_name: "FooParty(自由)"};
          var ticket2 =  {ticket_template_id: 2,  ticket_template_name: "FooParty(指定)"};
          dataStore.get("ticket_buffers").addTicket(ticket0);
          dataStore.get("ticket_buffers").addTicket(ticket1);
          dataStore.get("ticket_buffers").addTicket(ticket2);


          var target = _makeOne({service: service,  datastore: dataStore, appviews: {messageView: DummyMessageView}});
          dataStore.unbind("change:ticket_template_id");
          
          expect(dataStore.get("print_num", 3));
          target._printAllWithBuffer();
          expect(service.printAll.callCount).toEqual(2);
          expect(dataStore.get("print_num", 0));
        });
      });
    });
  });
  describe("TicketBuffer",  function(){
    var makeOne = function(){return TicketBuffer();};

    it("initial state", function(){
      var target = makeOne();
      var result = []
      target.consumeAll(function(buf, tid, name){ result.push(buf)});

      expect(result).toEqual(result, []);
    });

    it("add one", function(){
      var target = makeOne();
      var result = []

      var ticket = {ticket_template_id: 1, ticket_template_name: "ticket"};
      target.addTicket(ticket);
      target.consumeAll(function(buf, tid, name){ result.push(buf)});

      expect(result.length).toEqual(1);
      expect(result).toEqual([[ticket]])
    });
    it("add remove add", function(){
      var target = makeOne();
      var result = []

      var ticket = {ticket_template_id: 1, ticket_template_name: "ticket"};
      target.addTicket(ticket);
      target.removeTicket(ticket);
      target.addTicket(ticket);
      target.consumeAll(function(buf, tid, name){ result.push(buf)});

      expect(result.length).toEqual(1);
      expect(result).toEqual([[ticket]])
    });
    it("complex", function(){
      var target = makeOne();
      var result = []

      var ticket0 = {ticket_template_id: 1, ticket_template_name: "ticket"};
      target.addTicket(ticket0);
      var ticket1 = {ticket_template_id: 1, ticket_template_name: "ticket"};
      target.addTicket(ticket1);

      target.removeTicket(ticket0);
      target.consumeAll(function(buf, tid, name){ result.push(buf)});

      expect(result.length).toEqual(1);
      expect(result).toEqual([[ticket1]])
    });
  });
  describe("select printing ticket (ui)",  function(){
    var makeOne = function(opts){
      return new PrintableTicketsSelectView(opts);
    };

    it("draw printed ticket. this is checked", function(){
      var datastore = new DataStore();
      datastore.get("ticket_buffers").addTicket = jasmine.createSpy("");

      var ticket = {
        printed_at: Date(), 
        codeno: 1111, 
        ticket_name: "this-is-printed. not-checked", 
        ordered_product_item_token_id: 1
      };
      var result = makeOne({datastore: datastore})._createRow(ticket, 0)

      expect(result.find(":checked").length).toEqual(0);
      var ticketBuffer = datastore.get("ticket_buffers");
      expect(ticketBuffer.addTicket.callCount).toEqual(0);
    });
    it("draw unprinted ticket. this is not checked", function(){
      var datastore = new DataStore();
      datastore.get("ticket_buffers").addTicket = jasmine.createSpy("");

      var ticket = {
        printed_at: null, 
        codeno: 2111, 
        ticket_name: "this-is-unprinted-ticket", 
        ordered_product_item_token_id: 2
      };
      var result = makeOne({datastore: datastore})._createRow(ticket, 0)

      expect(result.find(":checked").length).toEqual(1);
      var ticketBuffer = datastore.get("ticket_buffers");
      expect(ticketBuffer.addTicket.callCount).toEqual(1);
    })
    it("after draw checked ticket is added", function(){
      var datastore = new DataStore();
      datastore.get("ticket_buffers").addTicket = jasmine.createSpy("");

      var tickets = [
        {
          printed_at: Date(), 
          codeno: 1111, 
          ticket_name: "printed1", 
          ordered_product_item_token_id: 1
        }, 
        {
          printed_at: Date(), 
          codeno: 1112, 
          ticket_name: "printed2", 
          ordered_product_item_token_id: 2
        }, 
        {
          codeno: 2111, 
          printed_at: null, 
          ticket_name: "unprinted", 
          ordered_product_item_token_id: 3
        }
      ];
      var doc = $('<div>').append('<div id="printable_tickets_box">');
      var target = makeOne({el: doc, datastore: datastore});
      target.draw(tickets);     

      var ticketBuffer = datastore.get("ticket_buffers");
      expect(ticketBuffer.addTicket.callCount).toEqual(1);
    });
    it("after draw. and toggle checkbox, ticket is removed from buffer", function(){
      var datastore = new DataStore();
      datastore.get("ticket_buffers").addTicket = jasmine.createSpy("");
      datastore.get("ticket_buffers").removeTicket = jasmine.createSpy("");

      var tickets = [
        {
          printed_at: Date(), 
          codeno: 1111, 
          ticket_name: "printed1", 
          ordered_product_item_token_id: 1
        }, 
        {
          printed_at: Date(), 
          codeno: 1112, 
          ticket_name: "printed2", 
          ordered_product_item_token_id: 2
        }, 
        {
          printed_at: null, 
          codeno: 2111, 
          ticket_name: "unprinted", 
          ordered_product_item_token_id: 3
        }
      ];
      var doc = $('<div>').append('<div id="printable_tickets_box">');
      var target = makeOne({el: doc, datastore: datastore});
      target.draw(tickets);     

      var ticketBuffer = datastore.get("ticket_buffers");
      expect(ticketBuffer.removeTicket.callCount).toEqual(0);

      var checked = target.$el.find('input[type="checkbox"]:checked').eq(0);
      checked.attr("checked", false);
      target.onToggleCheckBox(checked);

      expect(ticketBuffer.removeTicket.callCount).toEqual(1);
    });
  });
});