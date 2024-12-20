import pytest
import apteryx
from ncclient.xml_ import to_ele
from lxml import etree
from conftest import connect, _get_test_with_filter


def test_get_subtree_no_filter():
    m = connect()
    xml = m.get().data
    print(etree.tostring(xml, pretty_print=True, encoding="unicode"))
    # Full tree should be returned
    assert xml.find('./{*}test/{*}settings/{*}debug').text == 'enable'
    assert xml.find('./{*}test/{*}state/{*}counter').text == '42'
    assert xml.find('./{*}test/{*}animals/{*}animal/{*}name').text == 'cat'
    m.close_session()


@pytest.mark.skip(reason="exception creating RPC")
def test_get_subtree_empty_filter():
    m = connect()
    # ncclient does not allow empty filter strings - so make our own rpc
    rpc = """<get><filter type="subtree"></filter></get>"""

    xml = to_ele(m.rpc(to_ele(rpc)).xml)
    print(etree.tostring(xml, pretty_print=True, encoding="unicode"))
    # Nothing but an rpc-reply with an empty data attribute should be returned
    assert len(xml) and len(xml[0]) == 0
    m.close_session()


def test_get_subtree_node():
    select = '<test xmlns="http://test.com/ns/yang/testing"><settings><debug/></settings></test>'
    expected = """
<nc:data xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
    <test xmlns="http://test.com/ns/yang/testing">
        <settings>
            <debug>enable</debug>
        </settings>
    </test>
</nc:data>
    """
    _get_test_with_filter(select, expected)


# No default or prefixed namespace - we use the internal default namespace
def test_get_subtree_node_ns_none():
    select = '<test><settings><priority/></settings></test>'
    expected = """
<nc:data xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
    <test xmlns="http://test.com/ns/yang/testing">
        <settings>
            <priority>1</priority>
        </settings>
    </test>
</nc:data>
    """
    _get_test_with_filter(select, expected)


def test_get_subtree_node_ns_aug_none():
    select = '<test><settings><volume/></settings></test>'
    expected = """
<nc:data xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
    <test xmlns="http://test.com/ns/yang/testing">
        <settings>
            <volume>1</volume>
        </settings>
    </test>
</nc:data>
    """
    _get_test_with_filter(select, expected)


# Default namespace is the same as the internal default namespace
def test_get_subtree_node_ns_default():
    select = '<test xmlns="https://github.com/alliedtelesis/apteryx"><settings><priority/></settings></test>'
    expected = """
<nc:data xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
    <test xmlns="http://test.com/ns/yang/testing">
        <settings>
            <priority>1</priority>
        </settings>
    </test>
</nc:data>
    """
    _get_test_with_filter(select, expected)


def test_get_subtree_node_ns_aug_default():
    select = '<test xmlns="https://github.com/alliedtelesis/apteryx"><settings><volume/></settings></test>'
    expected = """
<nc:data xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
    <test xmlns="http://test.com/ns/yang/testing">
        <settings>
            <volume>1</volume>
        </settings>
    </test>
</nc:data>
    """
    _get_test_with_filter(select, expected)


# Default namespace is not the internal default namespace
def test_get_subtree_node_ns_other_no_prefix():
    select = '<test xmlns="http://test.com/ns/yang/testing-2"><settings><priority/></settings></test>'
    expected = """
<nc:data xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
    <test xmlns="http://test.com/ns/yang/testing-2">
        <settings>
            <priority>2</priority>
        </settings>
    </test>
</nc:data>
    """
    _get_test_with_filter(select, expected)


def test_get_subtree_node_ns_aug_other_no_prefix():
    select = '<test xmlns="http://test.com/ns/yang/testing-2"><settings><speed xmlns="http://test.com/ns/yang/testing2-augmented"/></settings></test>'
    expected = """
<nc:data xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
    <test xmlns="http://test.com/ns/yang/testing-2">
        <settings>
            <speed xmlns="http://test.com/ns/yang/testing2-augmented">2</speed>
        </settings>
    </test>
</nc:data>
    """
    _get_test_with_filter(select, expected)


# Prefixed namespace is not the internal default namespace
# Note that prefixes are not inherited, so must be specified on every node

def test_get_subtree_node_ns_other_prefix():
    select = '<t2:test xmlns:t2="http://test.com/ns/yang/testing-2"><t2:settings><t2:priority/></t2:settings></t2:test>'
    expected = """
<nc:data xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
    <test xmlns="http://test.com/ns/yang/testing-2">
        <settings>
            <priority>2</priority>
        </settings>
    </test>
</nc:data>
    """
    _get_test_with_filter(select, expected)


def test_get_subtree_node_ns_aug_other_prefix():
    select = '<t2:test xmlns:t2="http://test.com/ns/yang/testing-2" xmlns:aug2="http://test.com/ns/yang/testing2-augmented"><t2:settings><aug2:speed/></t2:settings></t2:test>'
    expected = """
<nc:data xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
    <test xmlns="http://test.com/ns/yang/testing-2">
        <settings>
            <speed xmlns="http://test.com/ns/yang/testing2-augmented">2</speed>
        </settings>
    </test>
</nc:data>
    """
    _get_test_with_filter(select, expected)


def test_get_subtree_empty():
    apteryx.set("/test/settings/empty", "empty")
    select = '<test><settings><empty/></settings></test>'
    expected = """
<nc:data xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
    <test xmlns="http://test.com/ns/yang/testing">
        <settings>
            <empty></empty>
        </settings>
    </test>
</nc:data>
    """
    _get_test_with_filter(select, expected)


def test_get_subtree_trunk():
    select = '<test><settings/></test>'
    expected = """
<nc:data xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
    <test xmlns="http://test.com/ns/yang/testing">
        <settings>
            <debug>enable</debug>
            <enable>true</enable>
            <priority>1</priority>
            <users>
                <name>bob</name>
                <age>34</age>
                <active>true</active>
                <groups>2</groups>
                <groups>23</groups>
            </users>
            <volume>1</volume>
        </settings>
    </test>
</nc:data>
    """
    _get_test_with_filter(select, expected)


def test_get_subtree_multi_parameters():
    select = '<test><settings><debug/><priority/></settings></test>'
    expected = """
<nc:data xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
    <test xmlns="http://test.com/ns/yang/testing">
        <settings>
            <debug>enable</debug>
            <priority>1</priority>
        </settings>
    </test>
</nc:data>
    """
    _get_test_with_filter(select, expected)


def test_get_subtree_list_container():
    select = '<test><animals/></test>'
    expected = """
<nc:data xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
  <test xmlns="http://test.com/ns/yang/testing">
    <animals>
      <animal>
        <name>cat</name>
        <type xmlns="http://test.com/ns/yang/animal-types">a-types:big</type>
      </animal>
      <animal>
        <name>dog</name>
        <colour>brown</colour>
      </animal>
      <animal>
        <name>hamster</name>
        <type xmlns="http://test.com/ns/yang/animal-types">a-types:little</type>
        <food>
          <name>banana</name>
          <type>fruit</type>
        </food>
        <food>
          <name>nuts</name>
          <type>kibble</type>
        </food>
      </animal>
      <animal>
        <name>mouse</name>
        <type xmlns="http://test.com/ns/yang/animal-types">a-types:little</type>
        <colour>grey</colour>
      </animal>
      <animal>
        <name>parrot</name>
        <type xmlns="http://test.com/ns/yang/animal-types">a-types:big</type>
        <colour>blue</colour>
        <toys>
          <toy>puzzles</toy>
          <toy>rings</toy>
        </toys>
      </animal>
    </animals>
  </test>
</nc:data>
    """
    _get_test_with_filter(select, expected)


def test_get_subtree_toplevel_list():
    apteryx.set("/test-list/1/index", "1")
    apteryx.set("/test-list/1/name", "cat")
    select = '<test-list/>'
    expected = """
<nc:data xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
    <test-list xmlns="http://test.com/ns/yang/testing">
      <index>1</index>
      <name>cat</name>
    </test-list>
</nc:data>
    """
    _get_test_with_filter(select, expected)


def test_get_subtree_toplevel_leaflist():
    apteryx.set("/test-leaflist/cat", "cat")
    apteryx.set("/test-leaflist/dog", "dog")
    select = '<test-leaflist/>'
    expected = """
<nc:data xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
    <test-leaflist xmlns="http://test.com/ns/yang/testing">cat</test-leaflist>
    <test-leaflist xmlns="http://test.com/ns/yang/testing">dog</test-leaflist>
</nc:data>
    """
    _get_test_with_filter(select, expected)


def test_get_subtree_list_element():
    select = '<test><animals><animal/></animals></test>'
    expected = """
<nc:data xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
  <test xmlns="http://test.com/ns/yang/testing">
    <animals>
      <animal>
        <name>cat</name>
        <type xmlns="http://test.com/ns/yang/animal-types">a-types:big</type>
      </animal>
      <animal>
        <name>dog</name>
        <colour>brown</colour>
      </animal>
      <animal>
        <name>hamster</name>
        <type xmlns="http://test.com/ns/yang/animal-types">a-types:little</type>
        <food>
          <name>banana</name>
          <type>fruit</type>
        </food>
        <food>
          <name>nuts</name>
          <type>kibble</type>
        </food>
      </animal>
      <animal>
        <name>mouse</name>
        <type xmlns="http://test.com/ns/yang/animal-types">a-types:little</type>
        <colour>grey</colour>
      </animal>
      <animal>
        <name>parrot</name>
        <type xmlns="http://test.com/ns/yang/animal-types">a-types:big</type>
        <colour>blue</colour>
        <toys>
          <toy>puzzles</toy>
          <toy>rings</toy>
        </toys>
      </animal>
    </animals>
  </test>
</nc:data>
    """
    _get_test_with_filter(select, expected)


def test_get_subtree_list_parameter():
    select = '<test><animals><animal><name/></animal></animals></test>'
    expected = """
<nc:data xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
  <test xmlns="http://test.com/ns/yang/testing">
    <animals>
      <animal>
        <name>cat</name>
      </animal>
      <animal>
        <name>dog</name>
      </animal>
      <animal>
        <name>hamster</name>
      </animal>
      <animal>
        <name>mouse</name>
      </animal>
      <animal>
        <name>parrot</name>
      </animal>
    </animals>
  </test>
</nc:data>
    """
    _get_test_with_filter(select, expected)


def test_get_subtree_selection_multi():
    select = '<test><animals><animal><name/><type/></animal></animals></test>'
    expected = """
<nc:data xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
  <test xmlns="http://test.com/ns/yang/testing">
    <animals>
      <animal>
        <name>cat</name>
        <type xmlns="http://test.com/ns/yang/animal-types">a-types:big</type>
      </animal>
      <animal>
        <name>dog</name>
      </animal>
      <animal>
        <name>hamster</name>
        <type xmlns="http://test.com/ns/yang/animal-types">a-types:little</type>
      </animal>
      <animal>
        <name>mouse</name>
        <type xmlns="http://test.com/ns/yang/animal-types">a-types:little</type>
      </animal>
      <animal>
        <name>parrot</name>
        <type xmlns="http://test.com/ns/yang/animal-types">a-types:big</type>
      </animal>
    </animals>
  </test>
</nc:data>
    """
    _get_test_with_filter(select, expected)


def test_get_subtree_select_one_node():
    select = '<test><animals><animal><name>cat</name></animal></animals></test>'
    expected = """
<nc:data xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
    <test xmlns="http://test.com/ns/yang/testing">
        <animals>
            <animal>
                <name>cat</name>
                <type xmlns="http://test.com/ns/yang/animal-types">a-types:big</type>
            </animal>
        </animals>
    </test>
</nc:data>
    """
    _get_test_with_filter(select, expected)


def test_get_subtree_select_one_with_colon():
    apteryx.set("/test/animals/animal/cat:ty/name", "cat:ty")
    apteryx.set("/test/animals/animal/cat:ty/type", "1")
    select = '<test><animals><animal><name>cat:ty</name></animal></animals></test>'
    expected = """
<nc:data xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
    <test xmlns="http://test.com/ns/yang/testing">
        <animals>
            <animal>
                <name>cat:ty</name>
                <type xmlns="http://test.com/ns/yang/animal-types">a-types:big</type>
            </animal>
        </animals>
    </test>
</nc:data>
    """
    _get_test_with_filter(select, expected)


def test_get_subtree_select_one_elements():
    select = '<test><animals><animal><name>cat</name><type/></animal></animals></test>'
    expected = """
<nc:data xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
    <test xmlns="http://test.com/ns/yang/testing">
        <animals>
            <animal>
                <name>cat</name>
                <type xmlns="http://test.com/ns/yang/animal-types">a-types:big</type>
            </animal>
        </animals>
    </test>
</nc:data>
    """
    _get_test_with_filter(select, expected)


def test_get_subtree_select_multi():
    select = """
<test>
  <animals>
    <animal>
      <name>cat</name>
    </animal>
    <animal>
      <name>dog</name>
    </animal>
  </animals>
</test>
    """
    expected = """
<nc:data xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
    <test xmlns="http://test.com/ns/yang/testing">
        <animals>
            <animal>
                <name>cat</name>
                <type xmlns="http://test.com/ns/yang/animal-types">a-types:big</type>
            </animal>
            <animal>
                <name>dog</name>
                <colour>brown</colour>
            </animal>
        </animals>
    </test>
</nc:data>
    """
    _get_test_with_filter(select, expected)


def test_get_subtree_select_attr_named_only():
    select = '<test><animals><animal name="cat"/></animals></test>'
    expected = """
<nc:data xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
    <test xmlns="http://test.com/ns/yang/testing">
        <animals>
            <animal>
                <name>cat</name>
                <type xmlns="http://test.com/ns/yang/animal-types">a-types:big</type>
            </animal>
        </animals>
    </test>
</nc:data>
    """
    _get_test_with_filter(select, expected)


def test_get_subtree_select_attr_named_element():
    select = '<test><animals><animal name="mouse"><type/></animal></animals></test>'
    expected = """
<nc:data xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
    <test xmlns="http://test.com/ns/yang/testing">
        <animals>
            <animal>
                <name>mouse</name>
                <type xmlns="http://test.com/ns/yang/animal-types">a-types:little</type>
            </animal>
        </animals>
    </test>
</nc:data>
    """
    _get_test_with_filter(select, expected)


def test_get_subtree_select_no_key_other_field():
    """
    Don't specify key node in filter. RFC states that we MAY include key in output,
    we are not currentl doing this.
    """
    select = '<test><animals><animal><type/></animal></animals></test>'
    expected = """
<nc:data xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
    <test xmlns="http://test.com/ns/yang/testing">
        <animals>
            <animal>
                <type xmlns="http://test.com/ns/yang/animal-types">a-types:big</type>
            </animal>
            <animal>
                <type xmlns="http://test.com/ns/yang/animal-types">a-types:little</type>
            </animal>
            <animal>
                <type xmlns="http://test.com/ns/yang/animal-types">a-types:little</type>
            </animal>
            <animal>
                <type xmlns="http://test.com/ns/yang/animal-types">a-types:big</type>
            </animal>
        </animals>
    </test>
</nc:data>
    """
    _get_test_with_filter(select, expected)


def test_get_subtree_select_no_key_other_field_value():
    """
    RFC states 'Filtering of list content is not supported.' This means that this query will return
    all types.
    """
    select = '<test><animals><animal><type>little</type></animal></animals></test>'
    expected = """
<nc:data xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
    <test xmlns="http://test.com/ns/yang/testing">
        <animals>
            <animal>
                <type xmlns="http://test.com/ns/yang/animal-types">a-types:big</type>
            </animal>
            <animal>
                <type xmlns="http://test.com/ns/yang/animal-types">a-types:little</type>
            </animal>
            <animal>
                <type xmlns="http://test.com/ns/yang/animal-types">a-types:little</type>
            </animal>
            <animal>
                <type xmlns="http://test.com/ns/yang/animal-types">a-types:big</type>
            </animal>
        </animals>
    </test>
</nc:data>
    """
    _get_test_with_filter(select, expected)


def test_get_subtree_select_key_other_field_value():
    """
    This test may not be showing correct behaviour.
    """
    select = '<test><animals><animal><name/><type>little</type></animal></animals></test>'
    expected = """
<nc:data xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
    <test xmlns="http://test.com/ns/yang/testing">
        <animals>
            <animal>
                <name>hamster</name>
                <type xmlns="http://test.com/ns/yang/animal-types">a-types:little</type>
            </animal>
            <animal>
                <name>mouse</name>
                <type xmlns="http://test.com/ns/yang/animal-types">a-types:little</type>
            </animal>
        </animals>
    </test>
</nc:data>
    """
    _get_test_with_filter(select, expected)


def test_get_subtree_select_key_value_other_field_value():
    """
    This test may not be showing correct behaviour.
    """
    select = """
<test>
    <animals>
        <animal>
            <name>mouse</name>
            <type>little</type>
        </animal>
    </animals>
</test>
    """
    expected = """
<nc:data xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
    <test xmlns="http://test.com/ns/yang/testing">
        <animals>
            <animal>
                <name>mouse</name>
                <type xmlns="http://test.com/ns/yang/animal-types">a-types:little</type>
            </animal>
        </animals>
    </test>
</nc:data>
    """
    _get_test_with_filter(select, expected)


def test_get_subtree_missing():
    select = '<test><animals><animal><name>elephant</name></animal></animals></test>'
    xml = _get_test_with_filter(select)
    assert xml.tag == '{urn:ietf:params:xml:ns:netconf:base:1.0}data'
    assert len(xml.getchildren()) == 0
    print(etree.tostring(xml, pretty_print=True, encoding="unicode"))


def test_get_multi_subtree_select_multi():
    select = """
<filter type="subtree">
<interfaces xmlns="http://example.com/ns/interfaces">
  <interface>
    <name>eth2</name>
  </interface>
</interfaces>
<test xmlns="http://test.com/ns/yang/testing">
  <animals>
    <animal>
      <name>cat</name>
    </animal>
    <animal>
      <name>dog</name>
    </animal>
  </animals>
</test>
</filter>
    """
    m = connect()
    xml = m.get(select).data
    print(etree.tostring(xml, pretty_print=True, encoding="unicode"))
    assert xml.find('./{*}test/{*}animals/{*}animal/{*}name').text == 'cat'
    assert xml.find('./{*}test/{*}animals/{*}animal[{*}name="cat"]/{*}type').text == 'a-types:big'
    assert xml.find('./{*}interfaces/{*}interface[{*}name="eth2"]/{*}mtu').text == '9000'
    m.close_session()


def test_get_subtree_select_key_value_other_field_exp_simple():
    select = """
<test>
    <animals>
        <animal>
            <name/>
                <colour>brown</colour>
        </animal>
    </animals>
</test>
    """
    expected = """
<nc:data xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
    <test xmlns="http://test.com/ns/yang/testing">
        <animals>
            <animal>
                <name>dog</name>
                <colour>brown</colour>
            </animal>
        </animals>
    </test>
</nc:data>
    """
    _get_test_with_filter(select, expected)


def test_get_subtree_select_key_value_other_field_exp_deep():
    select = """
<test>
    <animals>
        <animal>
            <name>hamster</name>
                <food>
                    <name/>
                        <type>kibble</type>
                </food>
        </animal>
    </animals>
</test>
    """
    expected = """
<nc:data xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
    <test xmlns="http://test.com/ns/yang/testing">
        <animals>
            <animal>
                <name>hamster</name>
                <food>
                    <name>nuts</name>
                    <type>kibble</type>
                </food>
            </animal>
        </animals>
    </test>
</nc:data>
    """
    _get_test_with_filter(select, expected)


def test_get_subtree_select_key_value_other_field_exp_two_results():
    select = """
<test>
    <animals>
        <animal>
            <name/>
                <type>1</type>
        </animal>
    </animals>
</test>
    """
    expected = """
<nc:data xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
    <test xmlns="http://test.com/ns/yang/testing">
        <animals>
            <animal>
                <name>cat</name>
                <type xmlns="http://test.com/ns/yang/animal-types">a-types:big</type>
            </animal>
            <animal>
                <name>parrot</name>
                <type xmlns="http://test.com/ns/yang/animal-types">a-types:big</type>
            </animal>
        </animals>
    </test>
</nc:data>
    """
    _get_test_with_filter(select, expected)


def test_get_subtree_select_interface():
    select = """
<filter type="subtree">
<interfaces xmlns="http://example.com/ns/interfaces">
  <interface>
    <name>eth2</name>
    <status></status>
  </interface>
</interfaces>
</filter>
    """
    m = connect()
    xml = m.get(select).data
    print(etree.tostring(xml, pretty_print=True, encoding="unicode"))
    assert xml.find('./{*}interfaces/{*}interface[{*}name="eth2"]/{*}status').text == 'not feeling so good'
    m.close_session()


def test_get_subtree_proxy_named_element():
    apteryx.set("/logical-elements/logical-element/loop/name", "loopy")
    apteryx.set("/logical-elements/logical-element/loop/root", "root")
    apteryx.set("/apteryx/sockets/E18FE205",  "tcp://127.0.0.1:9999")
    apteryx.proxy("/logical-elements/logical-element/loopy/*", "tcp://127.0.0.1:9999")
    select = '<logical-elements><logical-element><name>loopy</name><test><animals><animal name="mouse"><type/></animal></animals></test></logical-element></logical-elements>'
    expected = """
<nc:data xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
  <logical-elements xmlns="http://example.com/ns/logical-elements">
    <logical-element>
      <test xmlns="http://test.com/ns/yang/testing">
        <animals>
          <animal>
            <name>mouse</name>
            <type xmlns="http://test.com/ns/yang/animal-types">a-types:little</type>
          </animal>
        </animals>
      </test>
    </logical-element>
  </logical-elements>
</nc:data>
    """
    _get_test_with_filter(select, expected)


def test_get_subtree_if_feature():
    apteryx.set("/test/animals/animal/cat/friend", "smokey")
    apteryx.set("/test/animals/animal/cat/claws", "5")
    select = '<test><animals/></test>'
    expected = """
<nc:data xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
  <test xmlns="http://test.com/ns/yang/testing">
    <animals>
      <animal>
        <name>cat</name>
        <type xmlns="http://test.com/ns/yang/animal-types">a-types:big</type>
        <friend>smokey</friend>
      </animal>
      <animal>
        <name>dog</name>
        <colour>brown</colour>
      </animal>
      <animal>
        <name>hamster</name>
        <type xmlns="http://test.com/ns/yang/animal-types">a-types:little</type>
        <food>
          <name>banana</name>
          <type>fruit</type>
        </food>
        <food>
          <name>nuts</name>
          <type>kibble</type>
        </food>
      </animal>
      <animal>
        <name>mouse</name>
        <type xmlns="http://test.com/ns/yang/animal-types">a-types:little</type>
        <colour>grey</colour>
      </animal>
      <animal>
        <name>parrot</name>
        <type xmlns="http://test.com/ns/yang/animal-types">a-types:big</type>
        <colour>blue</colour>
        <toys>
          <toy>puzzles</toy>
          <toy>rings</toy>
        </toys>
      </animal>
    </animals>
  </test>
</nc:data>
    """
    _get_test_with_filter(select, expected)


def test_get_subtree_when_derived_from():
    apteryx.set("/test/animals/animal/cat/n-type", "big")
    select = '<test><animals><animal><name>cat</name></animal></animals></test>'
    expected = """
<nc:data xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
  <test xmlns="http://test.com/ns/yang/testing">
    <animals>
      <animal>
        <name>cat</name>
        <type xmlns="http://test.com/ns/yang/animal-types">a-types:big</type>
        <n-type>big</n-type>
      </animal>
    </animals>
  </test>
</nc:data>
    """
    _get_test_with_filter(select, expected)


def test_get_subtree_when_condition_true():
    apteryx.set("/test/animals/animal/wombat/name", "wombat")
    apteryx.set("/test/animals/animal/cat/claws", "5")
    select = '<test><animals><animal><name>cat</name></animal></animals></test>'
    expected = """
<nc:data xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
  <test xmlns="http://test.com/ns/yang/testing">
    <animals>
      <animal>
        <name>cat</name>
        <type xmlns="http://test.com/ns/yang/animal-types">a-types:big</type>
        <claws>5</claws>
      </animal>
    </animals>
  </test>
</nc:data>
    """
    _get_test_with_filter(select, expected)


def test_get_subtree_when_condition_false():
    apteryx.set("/test/animals/animal/cat/claws", "5")
    select = '<test><animals><animal><name>cat</name></animal></animals></test>'
    expected = """
<nc:data xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
  <test xmlns="http://test.com/ns/yang/testing">
    <animals>
      <animal>
        <name>cat</name>
        <type xmlns="http://test.com/ns/yang/animal-types">a-types:big</type>
      </animal>
    </animals>
  </test>
</nc:data>
    """
    _get_test_with_filter(select, expected)


def test_get_subtree_must_condition_true():
    apteryx.set("/test/animals/animal/dog/friend", "ben")
    select = '<test><animals><animal><name>dog</name></animal></animals></test>'
    expected = """
<nc:data xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
  <test xmlns="http://test.com/ns/yang/testing">
    <animals>
      <animal>
        <name>dog</name>
        <colour>brown</colour>
        <friend>ben</friend>
      </animal>
    </animals>
  </test>
</nc:data>
    """
    _get_test_with_filter(select, expected)


def test_get_subtree_must_condition_false():
    apteryx.set("/test/animals/animal/dog/friend", "ben")
    apteryx.prune("/test/animals/animal/cat")
    select = '<test><animals><animal><name>dog</name></animal></animals></test>'
    expected = """
<nc:data xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
  <test xmlns="http://test.com/ns/yang/testing">
    <animals>
      <animal>
        <name>dog</name>
        <colour>brown</colour>
      </animal>
    </animals>
  </test>
</nc:data>
    """
    _get_test_with_filter(select, expected)
