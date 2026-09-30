from kdp_factory.books.templates import template_for
from kdp_factory.kdp.validator import KDPValidator
def test_templates_have_core_fields():
    for kind in ("childrens","fiction","cookbook","custom"):
        t=template_for(kind); assert t["target_pages"]>=24 and "trim_size" in t
def test_validator_rejects_invalid_spec():
    issues=KDPValidator().validate_spec({"pages":10,"trim_size":"","language":""})
    assert any(x.code=="PAGE_COUNT" for x in issues)
    assert any(x.code=="TRIM_SIZE" for x in issues)
