from __future__ import unicode_literals
import boto

import sure  # noqa

from moto import mock_sns


@mock_sns
def test_creating_subscription():
    conn = boto.connect_sns()
    conn.create_topic("some-topic")
    topics_json = conn.get_all_topics()
    topic_arn = topics_json["ListTopicsResponse"]["ListTopicsResult"]["Topics"][0]['TopicArn']

    conn.subscribe(topic_arn, "http", "http://example.com/")

    subscriptions = conn.get_all_subscriptions()["ListSubscriptionsResponse"]["ListSubscriptionsResult"]["Subscriptions"]
    subscriptions.should.have.length_of(1)
    subscription = subscriptions[0]
    subscription["TopicArn"].should.equal(topic_arn)
    subscription["Protocol"].should.equal("http")
    subscription["SubscriptionArn"].should.contain(topic_arn)
    subscription["Endpoint"].should.equal("http://example.com/")

    # Now unsubscribe the subscription
    conn.unsubscribe(subscription["SubscriptionArn"])

    # And there should be zero subscriptions left
    subscriptions = conn.get_all_subscriptions()["ListSubscriptionsResponse"]["ListSubscriptionsResult"]["Subscriptions"]
    subscriptions.should.have.length_of(0)


@mock_sns
def test_getting_subscriptions_by_topic():
    conn = boto.connect_sns()
    conn.create_topic("topic1")
    conn.create_topic("topic2")

    topics_json = conn.get_all_topics()
    topics = topics_json["ListTopicsResponse"]["ListTopicsResult"]["Topics"]
    topic1_arn = topics[0]['TopicArn']
    topic2_arn = topics[1]['TopicArn']

    conn.subscribe(topic1_arn, "http", "http://example1.com/")
    conn.subscribe(topic2_arn, "http", "http://example2.com/")

    topic1_subscriptions = conn.get_all_subscriptions_by_topic(topic1_arn)["ListSubscriptionsByTopicResponse"]["ListSubscriptionsByTopicResult"]["Subscriptions"]
    topic1_subscriptions.should.have.length_of(1)
    topic1_subscriptions[0]['Endpoint'].should.equal("http://example1.com/")
