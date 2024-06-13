from pinhole.datasource.spiders.industry.apple import AppleSecurityBlog
from pinhole.datasource.spiders.industry.microsoft import MicrosoftSecurityBlog
from pinhole.models.openai import OpenaiChatModel, ChatContext
from pinhole.models.glm import GLMChatModel

model = GLMChatModel()

spider = MicrosoftSecurityBlog()
spider.start()
spider.join()
for doc in spider.collect():
    print(doc.title)
    print("=================")
    print("发布日期:", doc.date)
    ctx = ChatContext(model)
    resp = ctx.chat("请阅读以下文章内容并用中文给出简单总结，同时列出其中你认为最有价值的核心内容。\n\n" + doc.content.text)
    print(resp)
    print("")
