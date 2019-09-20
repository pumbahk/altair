# Requirements

* JRE 8 (or JDK 8): version 1.8.0_221
* maven 3.6.1

# Internal Libraries
ticket-printer has the following internal libraries in the dependencies. 

## batik-extension
path: `altair/batik-extension`

Library extending [Batik](https://xmlgraphics.apache.org/batik/), customized to preview and render SVG 

## ticketing-commons
path `altair/ticketing-commons`

Common utility library

# How to build
You need to install batik-extension and ticketing-commons ahead.

Both `altair-printing.exe` and `printing-${project.version}-jar-with-dependencies.jar` are generated in the directory named `target` after installing.

JRE 8 (or JDK 8) should be located in the same directory to run altair-printing.exe

```
cd ..

cd batik-extension
mvn install
cd ..

cd ticketing-commons
mvn install
cd ..

cd ticket-printer
mvn package
```
