import re


class SplitBillSlug:
    
    regex = r'(BILLS-\d{2,3})(([a-z]{2,})\d{1,})([a-z]{2,})'

    def __init__(self, bill_slug: str):
        regexed = re.match(self.regex, bill_slug)
        self.useless = regexed.group(1)
        self.bill_slug = regexed.group(2)
        self.bill_type = regexed.group(3)
        self.bill_title = str(regexed.group(3)).upper()
