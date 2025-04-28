from io import StringIO

from lapa_ng.naf import parse_naf


def test_naf_parser():
    xml = """<?xml version='1.0' encoding='UTF-8'?>
<NAF lang="nl" version="v4">
  <text>
    <wf>One</wf>
    <wf>two</wf>
  </text>
</NAF>
"""

    parser = list(parse_naf(StringIO(xml)))
    assert len(parser) == 2
    assert parser[0].text == "One"
    assert parser[1].text == "two"
