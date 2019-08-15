# requirements

* JRE 8 (or JDK 8): version 1.8.0_221
* maven 3.6.1 (and JRE 8+)

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
mvn package
```
