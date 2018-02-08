# requirements

* JRE 6 (or JDK 6)
* maven 3.3.3 (and JRE 7+)

# how to build

```
cd ..

cd batik-extension
mvn install
cd ..

cd ticketing-commons
mvn install
cd ..

cd ticket-printer
JRE6_HOME=/usr/local/jre1.6.0_45 mvn package
```
