#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#

"""
The Pulsar Python client library is based on the existing C++ client library.
All the same features are exposed through the Python interface.

Currently, the only supported Python version is 2.7.

## Install from PyPI

Download Python wheel binary files for MacOS and Linux
directly from the PyPI archive.

    #!shell
    $ sudo pip install pulsar-client

## Install from sources

Follow the instructions to compile the Pulsar C++ client library. This method
will also build the Python binding for the library.

To install the Python bindings:

    #!shell
    $ cd pulsar-client-cpp/python
    $ sudo python setup.py install

## Examples

### [Producer](#pulsar.Producer) example

    #!python
    import pulsar

    client = pulsar.Client('pulsar://localhost:6650')

    producer = client.create_producer(
                    'persistent://sample/standalone/ns/my-topic')

    for i in range(10):
        producer.send('Hello-%d' % i)

    client.close()

#### [Consumer](#pulsar.Consumer) Example

    #!python
    import pulsar

    client = pulsar.Client('pulsar://localhost:6650')
    consumer = client.subscribe(
            'persistent://sample/standalone/ns/my-topic',
            'my-sub')

    while True:
        msg = consumer.receive()
        print("Received message '%s' id='%s'", msg.data(), msg.message_id())
        consumer.acknowledge(msg)

    client.close()

### [Async producer](#pulsar.Producer.send_async) example

    #!python
    import pulsar

    client = pulsar.Client('pulsar://localhost:6650')

    producer = client.create_producer(
                    'persistent://sample/standalone/ns/my-topic',
                    block_if_queue_full=True,
                    batching_enabled=True,
                    batching_max_publish_delay_ms=10
                )

    def send_callback(res, msg):
        print('Message published res=%s', res)

    while True:
        producer.send_async('Hello-%d' % i, send_callback)

    client.close()
"""

import _pulsar

from _pulsar import Result, CompressionType, ConsumerType, PartitionsRoutingMode  # noqa: F401


class Message:
    """
    Message objects are returned by a consumer, either by calling `receive` or
    through a listener.
    """

    def data(self):
        """
        Returns a string with the content of the message.
        """
        return self._message.data()

    def properties(self):
        """
        Return the properties attached to the message. Properties are
        application-defined key/value pairs that will be attached to the
        message.
        """
        return self._message.properties()

    def partition_key(self):
        """
        Get the partitioning key for the message.
        """
        return self._message.partition_key()

    def publish_timestamp(self):
        """
        Get the timestamp in milliseconds with the message publish time.
        """
        return self._message.publish_timestamp()

    def message_id(self):
        """
        The message ID that can be used to refere to this particular message.
        """
        return self._message.message_id()


class Authentication:
    """
    Authentication provider object.
    """
    def __init__(self, dynamicLibPath, authParamsString):
        """
        Create the authentication provider instance.

        **Args**

        * `dynamicLibPath`: Path to the authentication provider shared library
          (such as `tls.so`)
        * `authParamsString`: Comma-separated list of provider-specific
          configuration params
        """
        self.auth = _pulsar.Authentication(dynamicLibPath, authParamsString)


class Client:
    """
    The Pulsar client. A single client instance can be used to create producers
    and consumers on multiple topics.

    The client will share the same connection pool and threads across all
    producers and consumers.
    """

    def __init__(self, service_url,
                 authentication=None,
                 operation_timeout_seconds=30,
                 io_threads=1,
                 message_listener_threads=1,
                 concurrent_lookup_requests=5000,
                 log_conf_file_path=None,
                 use_tls=False,
                 tls_trust_certs_file_path=None,
                 tls_allow_insecure_connection=False
                 ):
        """
        Create a new Pulsar client instance.

        **Args**

        * `service_url`: The Pulsar service url eg: pulsar://my-broker.com:6650/

        **Options**

        * `authentication`:
          Set the authentication provider to be used with the broker.
        * `operation_timeout_seconds`:
          Set timeout on client operations (subscribe, create producer, close,
          unsubscribe).
        * `io_threads`:
          Set the number of IO threads to be used by the Pulsar client.
        * `message_listener_threads`:
          Set the number of threads to be used by the Pulsar client when
          delivering messages through message listener. The default is 1 thread
          per Pulsar client. If using more than 1 thread, messages for distinct
          `message_listener`s will be delivered in different threads, however a
          single `MessageListener` will always be assigned to the same thread.
        * `concurrent_lookup_requests`:
          Number of concurrent lookup-requests allowed on each broker connection
          to prevent overload on the broker.
        * `log_conf_file_path`:
          Initialize log4cxx from a configuration file.
        * `use_tls`:
          Configure whether to use TLS encryption on the connection.
        * `tls_trust_certs_file_path`:
          Set the path to the trusted TLS certificate file.
        * `tls_allow_insecure_connection`:
          Configure whether the Pulsar client accepts untrusted TLS certificates
          from the broker.
        """
        conf = _pulsar.ClientConfiguration()
        if authentication:
            conf.authentication(authentication.auth)
        conf.operation_timeout_seconds(operation_timeout_seconds)
        conf.io_threads(io_threads)
        conf.message_listener_threads(message_listener_threads)
        conf.concurrent_lookup_requests(concurrent_lookup_requests)
        if log_conf_file_path:
            conf.log_conf_file_path(log_conf_file_path)
        conf.use_tls(use_tls)
        if tls_trust_certs_file_path:
            conf.tls_trust_certs_file_path(tls_trust_certs_file_path)
        conf.tls_allow_insecure_connection(tls_allow_insecure_connection)
        self._client = _pulsar.Client(service_url, conf)
        self._consumers = []

    def create_producer(self, topic,
                        send_timeout_millis=30000,
                        compression_type=CompressionType.NONE,
                        max_pending_messages=1000,
                        block_if_queue_full=False,
                        batching_enabled=False,
                        batching_max_messages=1000,
                        batching_max_allowed_size_in_bytes=128*1024,
                        batching_max_publish_delay_ms=10
                        ):
        """
        Create a new producer on a given topic.

        **Args**

        * `topic`:
          The topic name

        **Options**

        * `send_timeout_seconds`:
          If a message is not acknowledged by the server before the
          `send_timeout` expires, an error will be reported.
        * `compression_type`:
          Set the compression type for the producer. By default, message
          payloads are not compressed. Supported compression types are
          `CompressionType.LZ4` and `CompressionType.ZLib`.
        * `max_pending_messages`:
          Set the max size of the queue holding the messages pending to receive
          an acknowledgment from the broker.
        * `block_if_queue_full`: Set whether `send_async` operations should
          block when the outgoing message queue is full.
        * `message_routing_mode`:
          Set the message routing mode for the partitioned producer.
        """
        conf = _pulsar.ProducerConfiguration()
        conf.send_timeout_millis(send_timeout_millis)
        conf.compression_type(compression_type)
        conf.max_pending_messages(max_pending_messages)
        conf.block_if_queue_full(block_if_queue_full)
        conf.batching_enabled(batching_enabled)
        conf.batching_max_messages(batching_max_messages)
        conf.batching_max_allowed_size_in_bytes(batching_max_allowed_size_in_bytes)
        conf.batching_max_publish_delay_ms(batching_max_publish_delay_ms)
        p = Producer()
        p._producer = self._client.create_producer(topic, conf)
        return p

    def subscribe(self, topic, subscription_name,
                  consumer_type=ConsumerType.Exclusive,
                  message_listener=None,
                  receiver_queue_size=1000,
                  consumer_name=None,
                  unacked_messages_timeout_ms=None,
                  broker_consumer_stats_cache_time_ms=30000
                  ):
        """
        Subscribe to the given topic and subscription combination.

        **Args**

        * `topic`: The name of the topic.
        * `subscription`: The name of the subscription.

        **Options**

        * `consumer_type`:
          Select the subscription type to be used when subscribing to the topic.
        * `message_listener`:
          Sets a message listener for the consumer. When the listener is set,
          the application will receive messages through it. Calls to
          `consumer.receive()` will not be allowed. The listener function needs
          to accept (consumer, message), for example:

                #!python
                def my_listener(consumer, message):
                    # process message
                    consumer.acknowledge(message)

        * `receiver_queue_size`:
          Sets the size of the consumer receive queue. The consumer receive
          queue controls how many messages can be accumulated by the consumer
          before the application calls `receive()`. Using a higher value could
          potentially increase the consumer throughput at the expense of higher
          memory utilization. Setting the consumer queue size to zero decreases
          the throughput of the consumer by disabling pre-fetching of messages.
          This approach improves the message distribution on shared subscription
          by pushing messages only to those consumers that are ready to process
          them. Neither receive with timeout nor partitioned topics can be used
          if the consumer queue size is zero. The `receive()` function call
          should not be interrupted when the consumer queue size is zero. The
          default value is 1000 messages and should work well for most use
          cases.
        * `consumer_name`:
          Sets the consumer name.
        * `unacked_messages_timeout_ms`:
          Sets the timeout in milliseconds for unacknowledged messages. The
          timeout needs to be greater than 10 seconds. An exception is thrown if
          the given value is less than 10 seconds. If a successful
          acknowledgement is not sent within the timeout, all the unacknowledged
          messages are redelivered.
        * `broker_consumer_stats_cache_time_ms`:
          Sets the time duration for which the broker-side consumer stats will
          be cached in the client.
        """
        conf = _pulsar.ConsumerConfiguration()
        conf.consumer_type(consumer_type)
        if message_listener:
            conf.message_listener(message_listener)
        conf.receiver_queue_size(receiver_queue_size)
        if consumer_name:
            conf.consumer_name(consumer_name)
        if unacked_messages_timeout_ms:
            conf.unacked_messages_timeout_ms(unacked_messages_timeout_ms)
        conf.broker_consumer_stats_cache_time_ms(broker_consumer_stats_cache_time_ms)
        c = Consumer()
        c._consumer = self._client.subscribe(topic, subscription_name, conf)
        c._client = self
        self._consumers.append(c)
        return c

    def close(self):
        """
        Close the client and all the associated producers and consumers
        """
        self._client.close()


class Producer:
    """
    The Pulsar message producer, used to publish messages on a topic.
    """

    def send(self, content,
             properties=None,
             partition_key=None,
             replication_clusters=None,
             disable_replication=False
             ):
        """
        Publish a message on the topic. Blocks until the message is acknowledged

        **Args**

        * `content`:
          A string with the message payload

        **Options**

        * `properties`:
          A dict of application-defined string properties.
        * `partition_key`:
          Sets the partition key for message routing. A hash of this key is used
          to determine the message's destination partition.
        * `replication_clusters`:
          Override namespace replication clusters. Note that it is the caller's
          responsibility to provide valid cluster names and that all clusters
          have been previously configured as destinations. Given an empty list,
          the message will replicate according to the namespace configuration.
        * `disable_replication`:
          Do not replicate this message.
        """
        msg = self._build_msg(content, properties, partition_key,
                              replication_clusters, disable_replication)
        return self._producer.send(msg)

    def send_async(self, content, callback,
                   properties=None,
                   partition_key=None,
                   replication_clusters=None,
                   disable_replication=False
                   ):
        """
        Send a message asynchronously.

        The `callback` will be invoked once the message has been acknowledged
        by the broker.

        Example:

            #!python
            def callback(res, msg):
                print('Message published: %s' % res)

            producer.send_async(msg, callback)

        When the producer queue is full, by default the message will be rejected
        and the callback invoked with an error code.

        **Args**

        * `content`:
          A string with the message payload.

        **Options**

        * `properties`:
          A dict of application0-defined string properties.
        * `partition_key`:
          Sets the partition key for the message routing. A hash of this key is
          used to determine the message's destination partition.
        * `replication_clusters`: Override namespace replication clusters. Note
          that it is the caller's responsibility to provide valid cluster names
          and that all clusters have been previously configured as destinations.
          Given an empty list, the message will replicate per the namespace
          configuration.
        * `disable_replication`:
          Do not replicate this message.
        """
        msg = self._build_msg(content, properties, partition_key,
                              replication_clusters, disable_replication)
        self._producer.send_async(msg, callback)

    def close(self):
        """
        Close the producer.
        """

    def _build_msg(self, content, properties, partition_key,
                   replication_clusters, disable_replication):
        mb = _pulsar.MessageBuilder()
        mb.content(content)
        if properties:
            for k, v in properties:
                mb.property(k, v)
        if partition_key:
            mb.partition_key(partition_key)
        if replication_clusters:
            mb.replication_clusters(replication_clusters)
        if disable_replication:
            mb.disable_replication(disable_replication)
        return mb.build()


class Consumer:
    """
    Pulsar consumer.
    """

    def topic(self):
        """
        Return the topic this consumer is subscribed to.
        """
        return self._consumer.topic()

    def subscription_name(self):
        """
        Return the subscription name.
        """
        return self._consumer.subscription_name()

    def unsubscribe(self):
        """
        Unsubscribe the current consumer from the topic.

        This method will block until the operation is completed. Once the
        consumer is unsubscribed, no more messages will be received and
        subsequent new messages will not be retained for this consumer.

        This consumer object cannot be reused.
        """
        return self._consumer.unsubcribe()

    def receive(self, timeout_millis=None):
        """
        Receive a single message.

        If a message is not immediately available, this method will block until
        a new message is available.

        **Options**

        * `timeout_millis`:
          If specified, the receive will raise an exception if a message is not
          availble within the timeout.
        """
        if timeout_millis is None:
            return self._consumer.receive()
        else:
            return self._consumer.receive(timeout_millis)

    def acknowledge(self, message):
        """
        Acknowledge the reception of a single message.

        This method will block until an acknowledgement is sent to the broker.
        After that, the message will not be re-delivered to this consumer.

        **Args**

        * `message`:
          The received message or message id.
        """
        self._consumer.acknowledge(message)

    def acknowledge_cumulative(self, message):
        """
        Acknowledge the reception of all the messages in the stream up to (and
        including) the provided message.

        This method will block until an acknowledgement is sent to the broker.
        After that, the messages will not be re-delivered to this consumer.

        **Args**

        * `message`:
          The received message or message id.
        """
        self._consumer.acknowledge_cumulative(message)

    def pause_message_listener(self):
        """
        Pause receiving messages via the `message_listener` until
        `resume_message_listener()` is called.
        """
        self._consumer.pause_message_listener()

    def resume_message_listener(self):
        """
        Resume receiving the messages via the message listener.
        Asynchronously receive all the messages enqueued from the time
        `pause_message_listener()` was called.
        """
        self._consumer.resume_message_listener()

    def redeliver_unacknowledged_messages(self):
        """
        Redelivers all the unacknowledged messages. In failover mode, the
        request is ignored if the consumer is not active for the given topic. In
        shared mode, the consumer's messages to be redelivered are distributed
        across all the connected consumers. This is a non-blocking call and
        doesn't throw an exception. In case the connection breaks, the messages
        are redelivered after reconnect.
        """
        self._consumer.redeliver_unacknowledged_messages()

    def close(self):
        """
        Close the consumer.
        """
        self._consumer.close()
        self._client._consumers.remove(self)
