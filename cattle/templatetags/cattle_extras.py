from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def region_short(region):
    """地域名を漢字一文字に変換"""
    region_mapping = {
        '北海道': '北',
        '曽於': '曽',
        '飛騨': '飛',
        '自家': '自'
    }
    return region_mapping.get(region, region)

@register.filter
def intake_month(cow):
    """導入月を1桁の数字で返す"""
    if cow.intake_date:
        return str(cow.intake_date.month)
    return '-' 