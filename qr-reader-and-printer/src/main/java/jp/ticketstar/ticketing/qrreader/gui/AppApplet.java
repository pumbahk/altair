package jp.ticketstar.ticketing.qrreader.gui;

import java.io.IOException;
import java.net.URL;
import java.net.URLConnection;
import java.awt.Component;
import java.awt.Dimension;
import java.util.Arrays;
import java.util.Set;
import java.util.concurrent.CopyOnWriteArraySet;

import javax.swing.DefaultListCellRenderer;
import javax.swing.JApplet;
import javax.swing.JLabel;
import javax.swing.JList;

import jp.ticketstar.ticketing.ApplicationException;
import jp.ticketstar.ticketing.qrreader.AppModel;
import jp.ticketstar.ticketing.qrreader.TicketFormat;
import jp.ticketstar.ticketing.URLConnectionFactory;


import netscape.javascript.JSObject;

import com.github.mustachejava.Binding;
import com.github.mustachejava.Code;
import com.github.mustachejava.DefaultMustacheFactory;
import com.github.mustachejava.MustacheException;
import com.github.mustachejava.MustacheFactory;
import com.github.mustachejava.ObjectHandler;
import com.github.mustachejava.TemplateContext;
import com.github.mustachejava.reflect.ReflectionObjectHandler;
import com.github.mustachejava.util.GuardException;
import com.github.mustachejava.util.Wrapper;
import com.google.gson.JsonElement;
import com.google.gson.JsonParser;

class TicketFormatCellRenderer extends DefaultListCellRenderer {
	private static final long serialVersionUID = 1L;

	@Override
	public Component getListCellRendererComponent(JList list, Object value, int index, boolean isSelected, boolean cellHasFocus) {
		JLabel label = (JLabel)super.getListCellRendererComponent(list, value, index, isSelected, cellHasFocus);
		if (value != null)
			label.setText(((TicketFormat)value).getName());
		return label;
	}
}

class OurObjectHandler extends ReflectionObjectHandler {
	protected static class OurGuardedBinding implements Binding {
		private final ObjectHandler oh;
		private final TemplateContext tc;
		private final String name;
		private final Code code;
	
		public OurGuardedBinding(ObjectHandler oh, String name, TemplateContext tc, Code code) {
			this.name = name;
			this.code = code;
			this.oh = oh;
			this.tc = tc;
		}
	
		private Set<Wrapper> previousSet = new CopyOnWriteArraySet<Wrapper>();
		private volatile Wrapper[] prevWrappers;
	
		@Override
		public Object get(Object[] scopes) {
		    // Loop over the wrappers and find the one that matches
		    // this set of scopes or get a new one
		    Wrapper current = null;
		    Wrapper[] wrappers = prevWrappers;
		    if (wrappers != null) {
		        for (Wrapper prevWrapper : wrappers) {
		            try {
		                current = prevWrapper;
		                return oh.coerce(prevWrapper.call(scopes));
			        } catch (GuardException ge) {
			        	// Check the next one or create a new one
			        } catch (MustacheException me) {
			        	throw new MustacheException("Failed: " + current, me);
			        }
		        }
		    }
		    return createAndGet(scopes);
		}
	
		private Object createAndGet(Object[] scopes) {
			// Make a new wrapper for this set of scopes and add it to the set
			Wrapper wrapper = getWrapper(name, scopes);
			previousSet.add(wrapper);
			if (prevWrappers == null || prevWrappers.length != previousSet.size()) {
				prevWrappers = previousSet.toArray(new Wrapper[previousSet.size()]);
			}
			// If this fails the guard, there is a bug
			try {
				return oh.coerce(wrapper.call(scopes));
			} catch (GuardException e) {
				throw new AssertionError(
			          "Unexpected guard failure: " + previousSet + " " + Arrays.asList(scopes));
			}
		}
	
		protected synchronized Wrapper getWrapper(String name, Object[] scopes) {
			return oh.find(name, scopes);
		}
	}
	
	@Override
	public Binding createBinding(String name, TemplateContext tc, Code code) {
		return new OurGuardedBinding(this, name, tc, code);
	}	
}

/**
 * Created with IntelliJ IDEA.
 * User: mistat
 * Date: 8/9/12
 * Time: 10:00 PM
 * To change this template use File | Settings | File Templates.
 */
public class AppApplet extends JApplet implements IAppWindow, URLConnectionFactory {
	private static final long serialVersionUID = 1L;

	protected final MustacheFactory mustacheFactory;

	public AppApplet() {
		setPreferredSize(new Dimension(2147483647, 2147483647));
		final DefaultMustacheFactory mustacheFactory = new DefaultMustacheFactory();
		mustacheFactory.setObjectHandler(new OurObjectHandler());
		this.mustacheFactory = mustacheFactory;
	}
	
	AppAppletService appService;
	AppAppletModel model;
	AppAppletConfiguration config;

	public void unbind() {
		if (model == null)
			return;
	}
	
	public void bind(AppModel model) {
		unbind();
		model.refresh();
		this.model = (AppAppletModel)model;
	}

	private AppAppletConfiguration getConfiguration() throws ApplicationException {
		final AppAppletConfiguration config = new AppAppletConfiguration();
		final String endpointsJson = getParameter("endpoints");
		if (endpointsJson == null)
			throw new ApplicationException("required parameter \"endpoints\" not specified");
		final String cookie = getParameter("cookie");
		if (cookie == null)
			throw new ApplicationException("required parameter \"cookie\" not specified");
		config.cookie = cookie;
		config.callback = getParameter("callback");
		try {
			final JsonElement elem = new JsonParser().parse(endpointsJson);
			config.ticketTemplatesUrl = new URL(getCodeBase(), elem.getAsJsonObject().get("tickettemplates").getAsString());
			config.historyUrl = new URL(getCodeBase(), elem.getAsJsonObject().get("history").getAsString());
		} catch (Exception e) {
			throw new ApplicationException(e);
		}
		return config;
	}
	
	public URLConnection newURLConnection(final URL url) throws IOException {
		URLConnection conn = url.openConnection();
		conn.setRequestProperty("Cookie", config.cookie);
		conn.setUseCaches(false);
		conn.setAllowUserInteraction(true);
		return conn;
	}

	void populateModel() {
		final FormatLoader.LoaderResult result = new FormatLoader(this, mustacheFactory).fetchTicketTemplates(config);
		if (result.ticketTemplates.size() > 0) {
			model.getTicketTemplates().addAll(result.ticketTemplates);
			model.setTicketTemplate(result.ticketTemplates.get(0));
		}
	}

	public AppAppletService getService() {
		return appService;
	}
	
	public void init() {
		config = getConfiguration();
		model = new AppAppletModel();
    	appService = new AppAppletService(this, model);
		appService.setAppWindow(this);
		populateModel();
	
		if (config.callback != null) {
			try {
				JSObject.getWindow(this).call(config.callback, new Object[] { this });
			} catch (Exception e) {
				// any exception from the JS callback will be silently ignored.
				e.printStackTrace(System.err);
			}
		}
	}
}
