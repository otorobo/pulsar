
{% capture binary_release_url %}http://www.apache.org/dyn/closer.cgi/incubator/pulsar/pulsar-{{ site.current_version }}/apache-pulsar-{{ site.current_version }}-bin.tar.gz{% endcapture %}
{% capture source_release_url %}http://www.apache.org/dyn/closer.cgi/incubator/pulsar/pulsar-{{ site.current_version }}/apache-pulsar-{{ site.current_version }}-src.tar.gz{% endcapture %}

## System requirements

Pulsar is currently available for **MacOS** and **Linux**. In order to use Pulsar, you'll need to install [Java 8](http://www.oracle.com/technetwork/java/javase/downloads/jdk8-downloads-2133151.html).

## Installing Pulsar

To get started running Pulsar, download a binary tarball release in one of the following ways:

* by clicking one of these friendly buttons:

  <a href="{{ source_release_url }}" class="download-btn btn btn-lg" role="button" aria-pressed="true">Pulsar {{ site.current_version }} source release</a>
  <a href="{{ binary_release_url }}" class="download-btn btn btn-lg" role="button" aria-pressed="true">Pulsar {{ site.current_version }} binary release</a>

* from the Pulsar [downloads page](/download)
* from the Pulsar [releases page](https://github.com/apache/incubator-pulsar/releases/latest)
* using [wget](https://www.gnu.org/software/wget):

  ```shell
  # Source release
  $ wget http://archive.apache.org/dist/incubator/pulsar/pulsar-{{site.current_version}}/apache-pulsar-{{site.current_version}}-src.tar.gz

  # Binary release
  $ wget http://archive.apache.org/dist/incubator/pulsar/pulsar-{{site.current_version}}/apache-pulsar-{{site.current_version}}-bin.tar.gz
  ```

Once the tarball is downloaded, untar it and `cd` into the resulting directory:

```bash
# Source release
$ tar xvfz pulsar-{{ site.current_version }}-src.tar.gz
$ cd pulsar-{{ site.current_version }}

# Binary release
$ tar xvfz apache-pulsar-{{ site.current_version }}-bin.tar.gz
$ cd pulsar-{{ site.current_version }}
```

## What your package contains

Both the source and binary packages contain the following directories:

Directory | Contains
:---------|:--------
`bin` | Pulsar's [command-line tools](../../reference/CliTools), such as [`pulsar`](../../reference/CliTools#pulsar) and [`pulsar-admin`](../../reference/CliTools#pulsar-admin)
`conf` | Configuration files for Pulsar, including for [broker configuration](../../reference/Configuration#broker), [ZooKeeper configuration](../../reference/Configuration#zookeeper), and more
`data` | The data storage directory used by {% popover ZooKeeper %} and {% popover BookKeeper %}.
`lib` | The [JAR](https://en.wikipedia.org/wiki/JAR_(file_format)) files used by Pulsar.
`logs` | Logs created by the installation.

The source package contains all of the assets, specific to version {{ site.current_version}}, from the [Pulsar repository]({{ site.pulsar_repo }}).

## Compiling from source

If you've downloaded a source release and would like to compile it, you'll need to have [JDK 8](http://www.oracle.com/technetwork/java/javase/downloads/jdk8-downloads-2133151.html) and [Maven](https://maven.apache.org/) installed. To run the scripts in the `bin` directory, you'll need to have the [Java SE Runtime Environment](http://www.oracle.com/technetwork/java/javase/downloads/jre8-downloads-2133155.html) installed (JDK 8 already includes this).

To compile, skipping the tests:

```shell
$ mvn install -DskipTests
```
