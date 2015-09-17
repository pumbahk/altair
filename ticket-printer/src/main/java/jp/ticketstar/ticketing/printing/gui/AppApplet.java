package jp.ticketstar.ticketing.printing.gui;

import java.io.IOException;
import java.io.UnsupportedEncodingException;
import java.net.URL;
import java.net.URLConnection;
import java.awt.BorderLayout;
import java.awt.CardLayout;
import java.awt.Component;
import java.awt.Container;
import java.awt.Dimension;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.ComponentEvent;
import java.awt.event.ComponentListener;
import java.awt.event.ItemEvent;
import java.awt.event.ItemListener;
import java.awt.geom.AffineTransform;
import java.awt.geom.Dimension2D;
import java.beans.PropertyChangeEvent;
import java.beans.PropertyChangeListener;
import java.util.Arrays;
import java.util.Collection;
import java.util.List;
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Executors;
import java.util.concurrent.FutureTask;
import java.util.concurrent.ThreadFactory;
import java.util.logging.LogManager;

import javax.print.PrintService;
import javax.swing.ImageIcon;
import javax.swing.JApplet;
import javax.swing.JButton;
import javax.swing.JToggleButton;
import javax.swing.JComboBox;
import javax.swing.JList;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.JSplitPane;
import javax.swing.JToolBar;
import javax.swing.ListSelectionModel;
import javax.swing.SwingUtilities;
import javax.swing.event.ListDataEvent;
import javax.swing.event.ListDataListener;
import javax.swing.event.ListSelectionEvent;
import javax.swing.event.ListSelectionListener;

import jp.ticketstar.ticketing.ApplicationException;
import jp.ticketstar.ticketing.SerializingExecutor;
import jp.ticketstar.ticketing.printing.BoundingBoxOverlay;
import jp.ticketstar.ticketing.swing.GenericComboBoxModel;
import jp.ticketstar.ticketing.printing.GuidesOverlay;
import jp.ticketstar.ticketing.printing.AppModel;
import jp.ticketstar.ticketing.printing.JGVTComponent;
import jp.ticketstar.ticketing.printing.OurPageFormat;
import jp.ticketstar.ticketing.printing.Page;
import jp.ticketstar.ticketing.printing.PageEventListener;
import jp.ticketstar.ticketing.printing.PageSetModel;
import jp.ticketstar.ticketing.printing.StandardAppService;
import jp.ticketstar.ticketing.printing.TicketFormat;
import jp.ticketstar.ticketing.URLConnectionFactory;
import jp.ticketstar.ticketing.printing.gui.liveconnect.JSObjectPageEventListenerProxy;
import jp.ticketstar.ticketing.printing.gui.liveconnect.JSObjectPropertyChangeListenerProxy;

import org.apache.batik.swing.gvt.Overlay;

import netscape.javascript.JSObject;

import com.google.gson.JsonElement;
import com.google.gson.JsonParser;

import javax.swing.JSeparator;
import javax.swing.SwingConstants;

/**
 * Created with IntelliJ IDEA.
 * User: mistat
 * Date: 8/9/12
 * Time: 10:00 PM
 * To change this template use File | Settings | File Templates.
 */
public class AppApplet extends JApplet implements IAppWindow, URLConnectionFactory, ThreadFactory {
    /* patch */
    static {
        //reason:: https://redmine.ticketstar.jp/issues/6179
        try {
            Class.forName("jp.ticketstar.ticketing.gvt.font.FontFamilyResolverPatch");
        } catch(ClassNotFoundException ex){
            ex.printStackTrace();
        }
    }

    private static final long serialVersionUID = 1L;
    protected AppAppletService appService;
    protected AppAppletServiceImpl appServiceImpl;
    protected AppAppletModel model;
    protected AppAppletConfiguration config;
    protected boolean interactionEnabled = true;
    protected SerializingExecutor threadGenerator = new SerializingExecutor(Executors.defaultThreadFactory());

    //private JApplet frame;
    private JList list;
    private JPanel panel;
    private JLabel noPreviewImage;

    private GuidesOverlay guidesOverlay;
    private BoundingBoxOverlay boundingBoxOverlay;
    
    private ComponentListener centeringListener = new ComponentListener() {
        public void componentHidden(ComponentEvent e) {}

        public void componentMoved(ComponentEvent e) {}

        public void componentResized(ComponentEvent e) {
            final Dimension2D documentSize = model.getPageSetModel().getBridgeContext().getDocumentSize();
            final JGVTComponent source = (JGVTComponent)e.getSource();
            double ox = Math.max(0, (source.getWidth() - documentSize.getWidth()) / 2),
                   oy = Math.max(0, (source.getHeight() - documentSize.getHeight()) / 2);
            source.setPaintingTransform(new AffineTransform(1, 0, 0, 1, ox, oy));
        }

        public void componentShown(ComponentEvent e) {
            componentResized(e);
        }
    };

    private class PreviewImageRenderer implements Runnable{
        private PageSetModel pageSetModel;    
        public PreviewImageRenderer(PageSetModel pageSetModel){
            this.pageSetModel = pageSetModel;
        }
        public void runWithPreviewPage(){
            for (Page page: pageSetModel.getPages()) {
                final JGVTComponent gvtComponent = new JGVTComponent(false, false);
                {
                    @SuppressWarnings("unchecked")
                    Collection<Overlay> overlays = gvtComponent.getOverlays();
                    overlays.add(guidesOverlay);
                    overlays.add(boundingBoxOverlay);
                }
                gvtComponent.setPageFormat(model.getPageFormat());
                gvtComponent.addComponentListener(centeringListener);
                gvtComponent.setSize(new Dimension((int)panel.getWidth(), (int)panel.getHeight()));
                gvtComponent.setGraphicsNode(page.getGraphics());
                gvtComponent.setName(page.getName());
                panel.add(gvtComponent, page.getName());
            }
            pageSetModel.getPages().addListDataListener(new ListDataListener() {
                public void contentsChanged(ListDataEvent evt) {}

                public void intervalAdded(ListDataEvent evt) {}

                public void intervalRemoved(ListDataEvent evt) {
                    if (panel == null)
                        return;
                    final Component[] pageComponents = panel.getComponents();
                    for (int i = evt.getIndex0(), j = evt.getIndex1(); i <= j; i++) {
                        panel.remove(pageComponents[i]);
                    }
                    panel.validate();
                }
            });
        }
        public void runWithoutPreview(){
            panel.add(noPreviewImage,"no-preview");
        }
        public void run(){
            if (panel != null) {
                panel.removeAll();
                if(model.getPreviewEnable()){
                    runWithPreviewPage();
                }else {
                    runWithoutPreview();
                }
                panel.validate();
            }
            if (list != null)
                list.setModel(pageSetModel.getPages());
        }
    };

    private PropertyChangeListener pageSetModelChangeListener = new PropertyChangeListener() {
        public void propertyChange(PropertyChangeEvent evt) {
            if (evt.getNewValue() != null) {
                if (list != null)
                    list.clearSelection();
                final PageSetModel pageSetModel = (PageSetModel)evt.getNewValue();
                SwingUtilities.invokeLater(new PreviewImageRenderer(pageSetModel));
            }
        }
    };
    
    private PropertyChangeListener printServiceChangeListener = new PropertyChangeListener() {
        public void propertyChange(PropertyChangeEvent evt) {
            if (evt.getNewValue() != null) {
                if (comboBoxPrintService != null) {
                    PrintService printService = (PrintService)evt.getNewValue();
                    comboBoxPrintService.setSelectedItem(printService);
                }
            }
        }
    };
    private PropertyChangeListener printServicesChangeListener = new PropertyChangeListener() {
        public void propertyChange(PropertyChangeEvent evt) {
            if (evt.getNewValue() != null) {
                if (comboBoxPrintService != null) {
                    @SuppressWarnings("unchecked")
                    GenericComboBoxModel<PrintService> printServices = (GenericComboBoxModel<PrintService>)evt.getNewValue();
                    comboBoxPrintService.setModel(printServices);
                    if (printServices.size() > 0)
                        comboBoxPrintService.setSelectedIndex(0);
                }
            }
        }
    };
    private PropertyChangeListener pageFormatChangeListener = new PropertyChangeListener() {
        public void propertyChange(PropertyChangeEvent evt) {
            if (evt.getNewValue() != null && !model.getPrintingStatus()) {
                final OurPageFormat pageFormat = (OurPageFormat)evt.getNewValue();
                if (!config.embedded) {
                    for (final PrintService printService: model.getPrintServices()) {
                        if (printService.getName().equals(pageFormat.getPreferredPrinterName())) {
                            model.setPrintService(printService);
                            break;
                        }
                    }
                }
                if (comboBoxPageFormat != null)
                    comboBoxPageFormat.setSelectedItem(pageFormat);
            }
        }
    };
    private PropertyChangeListener pageFormatsChangeListener = new PropertyChangeListener() {
        public void propertyChange(PropertyChangeEvent evt) {
            if (evt.getNewValue() != null) {
                @SuppressWarnings("unchecked")
                GenericComboBoxModel<OurPageFormat> pageFormats = (GenericComboBoxModel<OurPageFormat>)evt.getNewValue();
                if (comboBoxPageFormat != null) {
                    comboBoxPageFormat.setModel(pageFormats);
                    if (pageFormats.size() > 0)
                        comboBoxPageFormat.setSelectedIndex(0);
                }
            }
        }
    };
    private PropertyChangeListener ticketFormatChangeListener = new PropertyChangeListener() {
        public void propertyChange(PropertyChangeEvent evt) {
            if (evt.getNewValue() != null && !model.getPrintingStatus()) {
                if (comboBoxTicketFormat != null) {
                    final TicketFormat ticketFormat = (TicketFormat)evt.getNewValue();
                    comboBoxTicketFormat.setSelectedItem(ticketFormat);
                }
            }
        }
    };
    private PropertyChangeListener ticketFormatsChangeListener = new PropertyChangeListener() {
        public void propertyChange(PropertyChangeEvent evt) {
            if (evt.getNewValue() != null) {
                if (comboBoxTicketFormat != null) {
                    @SuppressWarnings("unchecked")
                    GenericComboBoxModel<TicketFormat> ticketFormats = (GenericComboBoxModel<TicketFormat>)evt.getNewValue();
                    comboBoxTicketFormat.setModel(ticketFormats);
                    if (ticketFormats.size() > 0)
                        comboBoxTicketFormat.setSelectedIndex(0);
                }
            }
        }
    };
    private PropertyChangeListener printingStatusChangeListener = new PropertyChangeListener(){
        public void propertyChange(PropertyChangeEvent evt) {
            if (btnPrint != null)
                btnPrint.setEnabled(!model.getPrintingStatus());
        }
    };
    private PropertyChangeListener previewEnableChangeListener = new PropertyChangeListener(){
        public void propertyChange(PropertyChangeEvent evt){
            Boolean previewEnable = (Boolean)evt.getNewValue();
            Boolean willBeReDraw = true;
            if (previewEnable != null) {
                if(previewEnable && model.getPageSetModel().getPages().getSize() > 25){ // xxx: magic number.
                    appServiceImpl.displayError("発券枚数が多すぎるため、プレビューを有効にできません");
                    willBeReDraw = false;
                    model.setPreviewEnable(false);
                }
                if(willBeReDraw){
                    SwingUtilities.invokeLater(new PreviewImageRenderer(model.getPageSetModel()));
                }
            }
        }
    };
    private JButton btnPrint;
    private JToggleButton btnPreview;
    private JComboBox comboBoxPrintService;
    private JComboBox comboBoxPageFormat;
    private JComboBox comboBoxTicketFormat;
    private JSeparator separator;

    public void unbind() {
        if (model == null)
            return;
        model.removePropertyChangeListener(pageSetModelChangeListener);
        model.removePropertyChangeListener(printServicesChangeListener);
        model.removePropertyChangeListener(printServiceChangeListener);
        model.removePropertyChangeListener(pageFormatsChangeListener);
        model.removePropertyChangeListener(pageFormatChangeListener);
        model.removePropertyChangeListener(ticketFormatsChangeListener);
        model.removePropertyChangeListener(ticketFormatChangeListener);
        model.removePropertyChangeListener(printingStatusChangeListener);
        model.removePropertyChangeListener(previewEnableChangeListener);
    }
    
    public void bind(AppModel model) {
        unbind();
        model.addPropertyChangeListener("pageSetModel", pageSetModelChangeListener);
        model.addPropertyChangeListener("printServices", printServicesChangeListener);
        model.addPropertyChangeListener("printService", printServiceChangeListener);
        model.addPropertyChangeListener("pageFormats", pageFormatsChangeListener);
        model.addPropertyChangeListener("pageFormat", pageFormatChangeListener);
        model.addPropertyChangeListener("ticketFormats", ticketFormatsChangeListener);
        model.addPropertyChangeListener("ticketFormat", ticketFormatChangeListener);
        model.addPropertyChangeListener("printingStatus", printingStatusChangeListener);
        model.addPropertyChangeListener("previewEnable", previewEnableChangeListener);
        if (!config.embedded)
            model.refresh();
        this.model = (AppAppletModel)model;
    }

    public void setInteractionEnabled(boolean value) {
        final boolean prevValue = this.interactionEnabled;
        this.interactionEnabled = value;
        if (prevValue != value)
            this.setEnabled(value);
    }

    private AppAppletConfiguration getConfiguration() throws ApplicationException {
        final AppAppletConfiguration config = new AppAppletConfiguration();
        final String endpointsJson = getParameter("endpoints");
        if (endpointsJson == null)
            throw new ApplicationException("required parameter \"endpoints\" not specified");
        final String cookie = getParameter("cookie");
        if (cookie == null)
            throw new ApplicationException("required parameter \"cookie\" not specified");
        final String embedded = getParameter("embedded");
        config.cookie = cookie;
        config.embedded = embedded == null ? false: Boolean.valueOf(embedded);
        config.callback = getParameter("callback");
        try {
            final JsonElement elem = new JsonParser().parse(endpointsJson);
            config.formatsUrl = new URL(getCodeBase(), elem.getAsJsonObject().get("formats").getAsString());
            config.peekUrl = new URL(getCodeBase(), elem.getAsJsonObject().get("peek").getAsString());
            config.dequeueUrl = new URL(getCodeBase(), elem.getAsJsonObject().get("dequeue").getAsString());
        } catch (Exception e) {
            throw new ApplicationException(e);
        }
        return config;
    }

    public StandardAppService getService() {
        return appService;
    }
    
    public URLConnection newURLConnection(final URL url) throws IOException {
        URLConnection conn = url.openConnection();
        conn.setRequestProperty("Cookie", config.cookie);
        conn.setUseCaches(false);
        conn.setAllowUserInteraction(true);
        return conn;
    }

    protected void populateModel() {
        final FormatLoader.FormatPair formatPair = new FormatLoader(this).fetchFormats(config);
        if (formatPair.pageFormats.size() > 0) {
            model.getPageFormats().addAll(formatPair.pageFormats);
            model.setPageFormat(formatPair.pageFormats.get(0));
        }
        if (formatPair.ticketFormats.size() > 0) {
            model.getTicketFormats().addAll(formatPair.ticketFormats);
            model.setTicketFormat(formatPair.ticketFormats.get(0));
        }
    }

    public void init() {
        /*
        try {
            LogManager.getLogManager().readConfiguration(new java.io.ByteArrayInputStream("jp.ticketstar.handlers=java.util.logging.FileHandler\njp.ticketstar.level=FINEST\njava.util.logging.FileHandler.level=FINEST\njava.util.logging.FileHandler.pattern=/tmp/applet.log\njava.util.logging.FileHandler.formatter = java.util.logging.SimpleFormatter".getBytes("ASCII")));
        } catch (SecurityException e1) {
            e1.printStackTrace();
        } catch (UnsupportedEncodingException e1) {
            e1.printStackTrace();
        } catch (IOException e1) {
            e1.printStackTrace();
        }
        */
        config = getConfiguration();
        model = new AppAppletModel();
        appServiceImpl = new AppAppletServiceImpl(this, model);
        appService = new AppAppletService(appServiceImpl);
        
        if (!config.embedded) {
            initialize();
            guidesOverlay = new GuidesOverlay(model);
            boundingBoxOverlay = new BoundingBoxOverlay(model);
        }

        populateModel();
        appServiceImpl.setAppWindow(this);
        if (!config.embedded)
            appServiceImpl.doLoadTicketData(null);        

        if (config.callback != null) {
            try {
                JSObject.getWindow(this).call(config.callback, new Object[] { this });
            } catch (Exception e) {
                // any exception from the JS callback will be silently ignored.
                e.printStackTrace(System.err);
            }
        }
    }

    public void destroy() {
        threadGenerator.terminate();
        appService.dispose();
    }
    
    public void reload() {
        model.refresh();
    }
    
    /**
     * Initialize the contents of the frame.
     */
    private void initialize() {
        this.getContentPane().setLayout(new BorderLayout(0, 0));
        
        JToolBar toolBar = new JToolBar();
        toolBar.setFloatable(false);
        this.getContentPane().add(toolBar, BorderLayout.NORTH);
        
        comboBoxPageFormat = new JComboBox();
        comboBoxPageFormat.setRenderer(new PageFormatCellRenderer());
        comboBoxPageFormat.addItemListener(new ItemListener() {
            public void itemStateChanged(ItemEvent e) {
                model.setPageFormat((OurPageFormat)e.getItem());
            }
        });
        toolBar.add(comboBoxPageFormat);
        
        comboBoxTicketFormat = new JComboBox();
        comboBoxTicketFormat.setRenderer(new TicketFormatCellRenderer());
        comboBoxTicketFormat.addItemListener(new ItemListener() {
            public void itemStateChanged(ItemEvent e) {
                model.setTicketFormat((TicketFormat)e.getItem());
            }
        });
        toolBar.add(comboBoxTicketFormat);
        

        btnPreview = new JToggleButton("disable", false);
        btnPreview.addActionListener(new ActionListener(){
            public void actionPerformed(ActionEvent arg0) {
                Boolean enabled = btnPreview.isSelected();
                if (enabled){
                    btnPreview.setText("enable");
                } else{
                    btnPreview.setText("disable");
                }
                model.setPreviewEnable(enabled);
            }
        });

        noPreviewImage = new JLabel(new ImageIcon(AppWindow.class.getResource("/misc/nopreview.png")));

        btnPrint = new JButton("印刷");

        btnPrint.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent arg0) {
                appServiceImpl.printAll();
            }
        });

        comboBoxPrintService = new JComboBox();
        comboBoxPrintService.setRenderer(new PrintServiceCellRenderer());
        comboBoxPrintService.addItemListener(new ItemListener() {
            public void itemStateChanged(ItemEvent e) {
                model.setPrintService((PrintService)e.getItem());
            }
        });
        
        separator = new JSeparator();
        separator.setMaximumSize(new Dimension(4, 32767));
        separator.setOrientation(SwingConstants.VERTICAL);
        toolBar.add(separator);
        toolBar.add(comboBoxPrintService);

        toolBar.add(btnPreview);        

        btnPrint.setIcon(new ImageIcon(AppWindow.class.getResource("/toolbarButtonGraphics/general/Print24.gif")));
        toolBar.add(btnPrint);

        JSplitPane splitPane = new JSplitPane();
        this.getContentPane().add(splitPane, BorderLayout.CENTER);
        
        list = new JList();
        list.setPreferredSize(new Dimension(128, 0));
        list.setRequestFocusEnabled(false);
        list.setSelectionMode(ListSelectionModel.SINGLE_SELECTION);
        list.setCellRenderer(new TicketCellRenderer());
        list.addListSelectionListener(new ListSelectionListener() {
            public void valueChanged(ListSelectionEvent arg0) {
                final Page page = (Page)((JList)arg0.getSource()).getSelectedValue();
                if (page != null)
                    ((CardLayout)panel.getLayout()).show(panel, page.getName());
            }
        });
        splitPane.setLeftComponent(list);
        
        panel = new JPanel();
        panel.setLayout(new CardLayout());
        splitPane.setRightComponent(panel);
    }

    public Container getFrame() {
        return this;
    }

    public static PropertyChangeListener createPropertyChangeListenerProxy(JSObject jsobj) {
        return new JSObjectPropertyChangeListenerProxy(jsobj);
    }

    public static PageEventListener createPageEventListenerProxy(JSObject jsobj) {
        return new JSObjectPageEventListenerProxy(jsobj);
    }

    public static List<?> jsIntegerArrayToList(Integer[] jsobj) {
        return Arrays.asList(jsobj);
    }

    public static List<?> jsDoubleArrayToList(Double[] jsobj) {
        return Arrays.asList(jsobj);
    }

    public static List<?> jsStringArrayToList(String[] jsobj) {
        return Arrays.asList(jsobj);
    }

    public static List<?> jsObjectArrayToList(Object[] jsobj) {
        return Arrays.asList(jsobj);
    }

    public static void log(String level, String msg) {
        java.util.logging.Logger.getLogger(AppApplet.class.getName()).log(java.util.logging.Level.parse(level), msg);
    }

    public Thread newThread(final Runnable runnable) {
        final FutureTask<Thread> task = new FutureTask<Thread>(new Callable<Thread>() {
            @Override
            public Thread call() throws Exception {
                return new Thread(runnable);
            }
        });
        threadGenerator.execute(task);
        try {
            final Thread thread = task.get();
            return thread;
        } catch (ExecutionException e) {
            throw new IllegalStateException(e);
        } catch (InterruptedException e) {
            throw new IllegalStateException(e);
        }
    }

    public AppApplet() {
        setPreferredSize(new Dimension(2147483647, 2147483647));
        threadGenerator.start();
    }
}
