/*

   Licensed to the Apache Software Foundation (ASF) under one or more
   contributor license agreements.  See the NOTICE file distributed with
   this work for additional information regarding copyright ownership.
   The ASF licenses this file to You under the Apache License, Version 2.0
   (the "License"); you may not use this file except in compliance with
   the License.  You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

 */
package jp.ticketstar.ticketing.printing;

import java.io.InterruptedIOException;
import java.net.URLConnection;
import java.net.HttpURLConnection;

import org.apache.batik.bridge.DocumentLoader;
import org.apache.batik.swing.svg.SVGDocumentLoader;
import org.apache.batik.swing.svg.SVGDocumentLoaderEvent;
import org.apache.batik.swing.svg.SVGDocumentLoaderListener;
import org.apache.batik.util.EventDispatcher;
import org.apache.batik.util.EventDispatcher.Dispatcher;

import org.w3c.dom.svg.SVGDocument;

public class URLConnectionSVGDocumentLoader extends SVGDocumentLoader {
    /**
     * URLConnection
     */
    protected URLConnection conn;

    /**
     * Request body sender.
     */
    protected RequestBodySender sender;

    public URLConnectionSVGDocumentLoader(URLConnection conn, RequestBodySender sender, DocumentLoader loader) {
    	super(conn.getURL().toString(), loader);
        this.conn = conn;
        this.sender = sender;
    }

    /**
     * Runs this loader.
     */
    public void run() {
        final SVGDocumentLoaderEvent evt = new SVGDocumentLoaderEvent(this, null);
        try {
            fireEvent(startedDispatcher, evt);
            if (isHalted()) {
                fireEvent(cancelledDispatcher, evt);
                return;
            }

            if (sender != null) {
            	if (conn instanceof HttpURLConnection)
	            	((HttpURLConnection)conn).setRequestMethod(sender.getRequestMethod());
            	conn.setDoOutput(true);
            }
            conn.setDoInput(true);
            conn.connect();
            if (sender != null)
            	sender.send(conn.getOutputStream());

            SVGDocument svgDocument = (SVGDocument)loader.loadDocument(conn.getURL().toString(), conn.getInputStream());

            if (isHalted()) {
                fireEvent(cancelledDispatcher, evt);
                return;
            }

            fireEvent(completedDispatcher, new SVGDocumentLoaderEvent(this, svgDocument));
        } catch (InterruptedIOException e) {
            fireEvent(cancelledDispatcher, evt);
        } catch (Exception e) {
            exception = e;
            fireEvent(failedDispatcher, evt);
        } catch (ThreadDeath td) {
            exception = new Exception(td.getMessage());
            fireEvent(failedDispatcher, evt);
            throw td;
        } catch (Throwable t) {
            t.printStackTrace();
            exception = new Exception(t.getMessage());
            fireEvent(failedDispatcher, evt);
        }
    }

    public void fireEvent(Dispatcher dispatcher, Object event) {
        EventDispatcher.fireEvent(dispatcher, listeners, event, true);
    }

    static Dispatcher startedDispatcher = new Dispatcher() {
	        public void dispatch(Object listener,
	                             Object event) {
	            ((SVGDocumentLoaderListener)listener).documentLoadingStarted
	                ((SVGDocumentLoaderEvent)event);
	        }
	    };
            
    static Dispatcher completedDispatcher = new Dispatcher() {
            public void dispatch(Object listener,
                                 Object event) {
                ((SVGDocumentLoaderListener)listener).documentLoadingCompleted
                 ((SVGDocumentLoaderEvent)event);
            }
        };

    static Dispatcher cancelledDispatcher = new Dispatcher() {
            public void dispatch(Object listener,
                                 Object event) {
                ((SVGDocumentLoaderListener)listener).documentLoadingCancelled
                 ((SVGDocumentLoaderEvent)event);
            }
        };

    static Dispatcher failedDispatcher = new Dispatcher() {
            public void dispatch(Object listener,
                                 Object event) {
                ((SVGDocumentLoaderListener)listener).documentLoadingFailed
                 ((SVGDocumentLoaderEvent)event);
            }
        };
}
