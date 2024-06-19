from pinhole.datasource.spiders.academic.arxiv import ArxivSecurity, ArxivComputationLanguage
from pinhole.datasource.spiders.industry.apple import AppleSecurityBlog
from pinhole.datasource.spiders.industry.microsoft import MicrosoftSecurityBlog
from pinhole.datasource.spiders.community.lwn import LwnHeadline

from pinhole.datasource.spider import PinholeSpider

from typing import List, Type as Subtype

__all__ = ['all_spiders', 'PinholeSpider']

all_spiders: List[Subtype[PinholeSpider]] = [
    ArxivSecurity,
    ArxivComputationLanguage,
    AppleSecurityBlog,
    MicrosoftSecurityBlog,
    LwnHeadline
]
