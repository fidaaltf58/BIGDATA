# Image outils : client Hadoop 3.2.1 + Apache Flume 1.11.0 + Apache Sqoop 1.4.7
FROM bde2020/hadoop-base:2.0.0-hadoop3.2.1-java8

ENV FLUME_VERSION=1.11.0 \
    SQOOP_VERSION=1.4.7 \
    FLUME_HOME=/opt/flume \
    SQOOP_HOME=/opt/sqoop
ENV PATH=$PATH:$FLUME_HOME/bin:$SQOOP_HOME/bin

# --- Flume ---
RUN curl -fsSL https://archive.apache.org/dist/flume/${FLUME_VERSION}/apache-flume-${FLUME_VERSION}-bin.tar.gz \
      | tar -xz -C /opt \
 && mv /opt/apache-flume-${FLUME_VERSION}-bin $FLUME_HOME \
 # Conflit Guava : Flume embarque une ancienne Guava incompatible avec Hadoop 3 (NoSuchMethodError)
 && rm -f $FLUME_HOME/lib/guava-*.jar

# --- Sqoop ---
RUN curl -fsSL https://archive.apache.org/dist/sqoop/${SQOOP_VERSION}/sqoop-${SQOOP_VERSION}.bin__hadoop-2.6.0.tar.gz \
      | tar -xz -C /opt \
 && mv /opt/sqoop-${SQOOP_VERSION}.bin__hadoop-2.6.0 $SQOOP_HOME \
 # Driver JDBC MySQL 8
 && curl -fsSL -o $SQOOP_HOME/lib/mysql-connector-j-8.0.33.jar \
      https://repo1.maven.org/maven2/com/mysql/mysql-connector-j/8.0.33/mysql-connector-j-8.0.33.jar \
 # Sqoop 1.4.7 + Hadoop 3 : commons-lang 2.x manquant (NoClassDefFoundError StringUtils)
 && curl -fsSL -o $SQOOP_HOME/lib/commons-lang-2.6.jar \
      https://repo1.maven.org/maven2/commons-lang/commons-lang/2.6/commons-lang-2.6.jar \
 && cp $SQOOP_HOME/conf/sqoop-env-template.sh $SQOOP_HOME/conf/sqoop-env.sh \
 && echo "export HADOOP_COMMON_HOME=$HADOOP_HOME" >> $SQOOP_HOME/conf/sqoop-env.sh \
 && echo "export HADOOP_MAPRED_HOME=$HADOOP_HOME" >> $SQOOP_HOME/conf/sqoop-env.sh

WORKDIR /scripts
