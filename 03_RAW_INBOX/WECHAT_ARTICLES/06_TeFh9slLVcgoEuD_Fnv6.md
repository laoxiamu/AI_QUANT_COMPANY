# Claude Code 接入飞书的最全玩法，一篇文章全搞定

**URL:** https://mp.weixin.qq.com/s/TeFh9slLVcgoEuD_Fnv6NQ

**字数:** 9376

---

飞书 CLI 开源有一阵了。

我一直没写，其中一个原因是：

现在热点一个接一个，纯手搓有点顾不过来。

每天像鸡排哥一样，测完你的测你的哈哈哈......

![image](https://wsrv.nl/?url=https://mmbiz.qpic.cn/mmbiz_jpg/hAxuriaN9JIiczAwlCvAFWGibsqLa0UCMfMeIibMkibb5GD8jpe6icFKyXAJOjFqSYSu4h8nUfo3Nz9VbBe6RCcPFbucPDMf9EfsGHsKvBdQvsGEY/640?wx_fmt=jpeg&from=appmsg&watermark=1#imgIndex=0)

也是有时候明明说要写，但动不动就忘，我也承认这个习惯很不好。

但最重要的原因是，因为我之前用的是 OpenClaw 接飞书，用得挺好的，有点懒得换。

人都有惯性。一个东西能用了，就不太愿意去折腾别的。

后来主力切到 Claude Code 之后，我才想起来，飞书不是也开源了 CLI 吗？

然后又刷到博主

张咋啦

的视频，把 Claude Code 接进飞书当聊天机器人。两件事凑一起，我才认真花了时间去测。

测完只有一个感觉：应该早点装的。

目前跟「飞书 + Claude Code」有关的方案，我搜了很久，

这两种方法是最优质的。

一种是飞书官方开源的飞书 CLI，装上之后 Claude Code 能直接操控你飞书里的所有数据——多维表格、消息、文档、日历，全能动。

另一种是博主张咋啦做的开源项目，把 Claude Code 变成飞书里的聊天机器人，手机也能用，聊天记录也保存了。

两个我都试了，今天一起给大家讲。

01

飞书官方 CLI：让 AI 操控你的飞书数据

这个是飞书自己开源的，叫「飞书 CLI」。

![image](https://wsrv.nl/?url=https://mmbiz.qpic.cn/mmbiz_png/hAxuriaN9JI9TCVKSNJqjnIQ94ddVax7ZPrAjg2PqNNDTAgd76WYsibz0oib2PfCa8ticwlvSozkowxuG44WEZMg5pr5ibhy3JazQ4UJDd8JJ1LQ/640?wx_fmt=png&from=appmsg&watermark=1#imgIndex=1)

地址在这里：

https://github.com/larksuite/cli

可能有人不知道CLI是什么，这里简单科普一下：

CLI 全称 Command Line Interface，翻译过来就是“命令行”。听着挺唬人的，但其实很简单。

你平时用电脑，是不是都靠点图标、点按钮？打开微信双击图标，发消息点输入框打字再点发送。这叫图形界面（GUI），你能看到按钮在哪，点就完了。

CLI 换了个方式：没有图标，没有按钮，就一个黑框框，你打字告诉电脑要干什么，它就干什么。

就像你去饭店吃饭，一个是看菜单勾选（图形界面），一个是直接冲后厨喊：“宫保鸡丁不要花生！”（命令行）。

效果一样，就是入口不同。

所以「飞书 CLI」的意思就是：你可以通过打命令的方式，让 Claude Code 去操作你飞书里的东西。

它解决的核心问题是：Claude Code 终于能碰到你飞书里的数据了。

以前 Claude Code 只能在你本地文件夹里转悠。它能读你电脑上的代码、改你电脑上的文件，但它碰不到你飞书里的多维表格、碰不到你的飞书消息、碰不到你的项目管理看板。

装上飞书 CLI 之后，这些全打通了。

安装方式很简单：

直接跟你的 Claude Code 说一句话就行：

帮我装一下所有的东西：

https://github.com/larksuite/cli/blob/main/README.zh.md

它会自动把飞书 CLI 和 26 个 Skills 一起装好。中间需要扫码授权一下飞书账号，跟着走就行。

![image](https://wsrv.nl/?url=https://mmbiz.qpic.cn/mmbiz_png/hAxuriaN9JIibPkXzoLBtdtpF9ff6JNh1HEghEyd6PPPL0eicvC1yEVC2B5Ew9KeJRTib1vOTEWAHVGNnDScoSofIcicSYQQAJ3NSxO3w5u9icAQ8/640?wx_fmt=png&from=appmsg&watermark=1#imgIndex=2)

等一会会跳出一个链接，单击链接直接跳转。

会弹出一个创建飞书CLI应用的界面，设置你喜欢的头像和名称，点击创建。

![image](https://wsrv.nl/?url=https://mmbiz.qpic.cn/mmbiz_png/hAxuriaN9JIic7BnOejeh7hEGeLFeTFCib5SXF4ncAy3BNbqDJn8p431EibS0qiabzPcpO6gRnapogbPbWB5bQQXasibFibLLZZ9icf7EDQFXe0ZzWs/640?wx_fmt=png&from=appmsg&watermark=1#imgIndex=3)

显示这个界面就是创建成功。

![image](https://wsrv.nl/?url=https://mmbiz.qpic.cn/mmbiz_png/hAxuriaN9JIicF24cyMhGia2CszydNNNsuJzAFzvm7FSVlfpn6OvArZEICZLw5mkXHQlfjbiaUTq2QxGyvAq6bjykMHC4mpvQnNXibcE1r7wAoZ0/640?wx_fmt=png&from=appmsg&watermark=1#imgIndex=4)

然后飞书会弹出一个消息，到这一步就创建完成。

![image](https://wsrv.nl/?url=https://mmbiz.qpic.cn/sz_mmbiz_jpg/hAxuriaN9JI9SykCCpbWWoRWIxFajbJTianZZTHKLK07Tmt5icUFFsvrPpLTjib6KSma9GibedRKfEiaXjOogzcAJIGoiaKia9w2Ndiceibww47UqvFng/640?wx_fmt=jpeg&from=appmsg&watermark=1#imgIndex=5)

然后 Claude 会继续第三步登录授权，等就行。

![image](https://wsrv.nl/?url=https://mmbiz.qpic.cn/mmbiz_png/hAxuriaN9JIibYo2qe4JkiaQsEF9FFIgEVn05XzHd9Yial5ETtKuYQrs4paD11JQpibcYiaicicYlmFvafPyxLuj1ZYcfZLNGnlpPzh1GG3HKIXDct4/640?wx_fmt=png&from=appmsg&watermark=1#imgIndex=6)

然后会继续弹出一个网址，进入这个页面，点击开通并授权全部内容。

![image](https://wsrv.nl/?url=https://mmbiz.qpic.cn/sz_mmbiz_png/hAxuriaN9JI8GlbgAcAYpQYict56XxwpWe4qCUKhNP38Jp6WOMz0Lxkn6iaor6JtduJUH66sjYZqljL7oicuaBjFjxG7Qvc9ZsxXfz0NcOhjKrE/640?wx_fmt=png&from=appmsg&watermark=1#imgIndex=7)

最后 Claude 显示安装完成。恭喜你，开始纵享丝滑。

![image](https://wsrv.nl/?url=https://mmbiz.qpic.cn/mmbiz_jpg/hAxuriaN9JIibFb87YWCB0QVII3fhvOeZShCwD0mPaJKzEzC1EcFHl09EQVbPTUCRFbm2gQXTfLneU7n80CGxUCpdIAB2OlFc50iaWjVVKiadQI/640?wx_fmt=jpeg&from=appmsg&watermark=1#imgIndex=8)

等等，其实还有最最后一步：重启你的 Claude 或者其他 Agent 产品，一定记得！

02

它都能干什么？

装好就等不急了，我先替大家玩一下。

先试试最基础的群发消息。

因为飞书可能有很多组织，我先让它查一下安装的组织名称，以免搞错了。

![image](https://wsrv.nl/?url=https://mmbiz.qpic.cn/sz_mmbiz_png/hAxuriaN9JIib7pMNicPcJmRO7237KLtPDlqoOb3D9tav1VXwoUQf03gtDPxh6Hvcqj55GAibpiaQFBwqxZkChicVDdzfXlfwicHc7GGtIjpko2udY/640?wx_fmt=png&from=appmsg&watermark=1#imgIndex=9)

它会帮你找到你对应的组织。

![image](https://wsrv.nl/?url=https://mmbiz.qpic.cn/mmbiz_jpg/hAxuriaN9JIibicpJglpRnzMPnLtiaMNM8CtMtbZ9HyLrnj005iaicQQ6x5hm4rHho0cB5o425RV0QV7qwywXUYUr1tK8vGD0ichqt580GNlSMiaBPc/640?wx_fmt=jpeg&from=appmsg&watermark=1#imgIndex=10)

Claude 自己检索了大概1min，直接发送，丝滑！然后他们就收到了我的消息。

![image](https://wsrv.nl/?url=https://mmbiz.qpic.cn/mmbiz_jpg/hAxuriaN9JIibp4Tj7NPxic85Asibp03aNjOJsAE9gCGgLWRvM8gy1PWfMowv6GVzRHmFg2vjWL5N6iboZbTyoZVicG1ngUfEqX9l1NJAEibfsXVSY/640?wx_fmt=jpeg&from=appmsg&watermark=1#imgIndex=11)

![image](https://wsrv.nl/?url=https://mmbiz.qpic.cn/sz_mmbiz_jpg/hAxuriaN9JIic5sw2IZ2bHXxFq9bKDw76K6YWUuPo3Qd0Jlh9pVxiaKPzib71FnoeUkxWArLnMtgpAnHia1ia6wI97AQWHjONmHQ2tsTZ9ewJdfFg/640?wx_fmt=jpeg&from=appmsg&watermark=1#imgIndex=12)

除此之外，我一直想解决一个很棘手的问题，倒也不是困难，就是很麻烦。

我知道很多小伙伴是因为小宇宙播客关注到我，我每天会把小宇宙【AI圈儿】中内容的文字版发到我们自己的社群里，供大家参考阅读。

但微信直接发大段文字会被折叠，所以每天我们小伙伴是直接发word文稿。之前总是懒，让openclaw整理发出来，结果每次都宕机，也返回不出文档。

我干脆让 Claude 试试。

在这里做个小插曲：为了方便大家阅读，我在内部做了一个【AI圈儿】的网站，完全免费开放，每天汇总我们精选的AI热点。

网站目前还在内部调试中，预计下周一上线，被迫继续加班......

先看看预览图：

![image](https://wsrv.nl/?url=https://mmbiz.qpic.cn/sz_mmbiz_png/hAxuriaN9JIicwTt6kG5iccjCVgk7D6EA93lib7zCS6TmFsKWWB7mVUFj2UQFfibCKSCb18A9Z3hOyxC0lGDgDv6UXlKJwW1pDkEl3ia9BsMRNeNw/640?wx_fmt=png&from=appmsg&watermark=1#imgIndex=13)

为了测试功能，我直接尝试飞书日报的形式。

所以我告诉Claude：

![image](https://wsrv.nl/?url=https://mmbiz.qpic.cn/mmbiz_png/hAxuriaN9JI9fMeWspj7IGcFbexSa4Jz6MKlf31q6ZE206icjDFTTN5vGgqGGXGamgCFaWw5dugX1ibtYh9cVLMdEoR4WKgSXJtohr5co418Uc/640?wx_fmt=png&from=appmsg&watermark=1#imgIndex=14)

然后它会先设计方案（比如分几个步骤，每个步骤干啥），然后执行，中间需要你手动开权限的地方也会提醒你。

![image](https://wsrv.nl/?url=https://mmbiz.qpic.cn/sz_mmbiz_png/hAxuriaN9JIicIOrlFibZXHfAgbrMk0Fz6vHN8LFJj78G2gDxqWIDnCx8sQvJk12dBDBMyY3ia2icPnhIDU24sian3U24bia1m2CGzIWKCicB9ratn8/640?wx_fmt=png&from=appmsg&watermark=1#imgIndex=15)

最后，整个流程跑通了。

![image](https://wsrv.nl/?url=https://mmbiz.qpic.cn/mmbiz_jpg/hAxuriaN9JI8HOsGolddvLK3veSlZqAWr9yBZ7ibPHU4C6G2lZZChvEBkIAKCQk82Y1mIzZKRfC1TnHPqXVAESSCGjkjwiam6vtgbL1XZQ7ibWI/640?wx_fmt=jpeg&from=appmsg&watermark=1#imgIndex=16)

第一次可能会慢点，因为 Claude 需要时间设计方案。后面你再跑这个流程，只需要按方案执行，会很快。

⭐我也把这个部分内容建成了一个临时的飞书云文档，大家可以直接访问，获取每日的AI热点资讯~（后面会配套网站一起）

飞书云文档链接在这：

https://lcn2csfclcca.feishu.cn/wiki/UEjIwWgd0iDJJLkJ9P5cGHHxnTG

03

飞书 Bridge：把 Claude Code 变成飞书聊天机器人

飞书 CLI 解决了“AI 操控飞书数据”的问题，但还有一个痛点没解决：

你只能在电脑前面用 Claude Code。

出门开会、在外面吃饭、躺在床上想起来一个活儿，想让它帮你干，没办法。终端在电脑上，电脑在桌上，你人不在桌前，就什么都干不了。

还有一个问题。

我在终端里跟 Claude Code 聊了一下午，关掉窗口，聊天记录就没了。我不敢关终端标签页，越攒越多，最后自己都分不清哪个是哪个。

飞书 Bridge 就是来解决这两个问题的。

这个方案来自博主“张咋啦”的开源项目：飞书 coding-agent-bridge

![image](https://wsrv.nl/?url=https://mmbiz.qpic.cn/mmbiz_png/hAxuriaN9JIib6f7jH7iakdkUKBOxqpa7uMfnjvBNpS6YjKevQcuYEEvy2XMUicVfc2TX5KpAnOiafGbZhE4VuqdtRwGRmib7doLSaVckWxDPibrx8/640?wx_fmt=png&from=appmsg&watermark=1#imgIndex=17)

链接在这：

https://github.com/zarazhangrui/feishu-claude-code-bridge

她在仓库里也写得很明白，就是方便你直接把飞书的消息转发到本地的Claude/Codex上，继续工作。

而且每个任务有自己的对话，不用担心混在一起。

![image](https://wsrv.nl/?url=https://mmbiz.qpic.cn/sz_mmbiz_png/hAxuriaN9JI8VHjKCwxIa8tlrlsD9qxhDy67938YNWISQTWGo5sQAO0Qe4TjJa3o7KEpibY9eAfDaqswfVjibLjc2E1ANoaQFn9DkzkGJzhb9s/640?wx_fmt=png&from=appmsg&watermark=1#imgIndex=18)

安装方式和其他skill一样。复制链接，直接告诉Claude安装。

安装完成会有提示。

![image](https://wsrv.nl/?url=https://mmbiz.qpic.cn/sz_mmbiz_png/hAxuriaN9JIicSwCErMp9MR8D6kg2ZzR0wooDqeaY6JKEeAeKFNbcV55geRTH9riavDKmr4rxgialJMQvZjMtcq1zhRqxF3990q1SFsVnrmBDP4/640?wx_fmt=png&from=appmsg&watermark=1#imgIndex=19)

这时候需要新启动一个cmd输入下面的代码：

lark-channel-bridge run

输入后会弹出一个二维码和网站，手机扫码或者点击链接均可设置。

![image](https://wsrv.nl/?url=https://mmbiz.qpic.cn/sz_mmbiz_jpg/hAxuriaN9JI8HQHpibGPLCKEMRKUkOlWXkBia6YXC32Z1f1JntGOx6YBldww8vCbfKtr87LBHvrE208ow5IbU4Aeic7I2b03GG4ZXkMG5lobI1A/640?wx_fmt=jpeg&from=appmsg&watermark=1#imgIndex=20)

在飞书开放平台，不用新建联系人，可以选择已有应用（在方法1中建立的飞书机器人）。

点击确认添加。

![image](https://wsrv.nl/?url=https://mmbiz.qpic.cn/sz_mmbiz_png/hAxuriaN9JIicBIQ66vTdDGEHLy7bmjSiciaqyrXrrPlPoMLRhOaoibdQiaVjP8B71IZw1erTnrcvMDVmRXH3dgWEL4vQdecZwctc9j81AXHDlpiaM/640?wx_fmt=png&from=appmsg&watermark=1#imgIndex=21)

显示配置成功即可。

![image](https://wsrv.nl/?url=https://mmbiz.qpic.cn/mmbiz_png/hAxuriaN9JI90Uknokj8n7GuMPDbTk2xtWtYCicmzukZN2HqXQvOzfia09kKJ8tBIbcX5lbzukN9BfrlDnMLD5Pp7KNpZDiad6etTXgXfA2YWt0/640?wx_fmt=png&from=appmsg&watermark=1#imgIndex=22)

装好之后，Claude Code 变成了你飞书里的一个联系人。你可以像跟同事一样给它发消息，它秒回。

![image](https://wsrv.nl/?url=https://mmbiz.qpic.cn/sz_mmbiz_png/hAxuriaN9JI8icGml3D9BVQADDo2ib91JkS5tLV42atlju5VmRxEwQRr1ySzfM1Kic1JDD3RzFko1JhZSHOjYfDm5SZIqTOfHh51QWPsPHAPXJg/640?wx_fmt=png&from=appmsg&watermark=1#imgIndex=23)

手机也能用了。

在外面开会、吃饭、躺床上，直接打开手机飞书给它发消息派任务。

Mac 用户配合 Amphetamine 这个 App，电脑合盖也不会休眠，等于你的 Claude Code 7×24 小时在线。

![image](https://wsrv.nl/?url=https://mmbiz.qpic.cn/sz_mmbiz_jpg/hAxuriaN9JI9Xney50wna5NS5qia6pDhY3s1OICuw4MzsLXF1NZxxia455ic7OGzTYribe5WELJqy1HfMUao2p6ib1iapgtMoJlA8dytxbl3lRg2FI/640?wx_fmt=jpeg&from=appmsg&watermark=1#imgIndex=24)

以前在终端里用 Claude Code，你经常会开十几个 tab，乱到自己找不到。接入飞书之后，一个任务就是一个群。

想建新群？直接跟它说

/new chat

，告诉它这个群干嘛的，它自动帮你拉。

在飞书设置里给所有 Claude 群加一个“claude”标签，一键筛出来，飞书秒变终端。

04

简单总结一下

我之前一直觉得 Claude Code 有个巨大的短板：它被困在终端里。

只能在电脑前面用，只能通过命令行交互，关了窗口记录就没了，碰不到你日常工作里的数据。

虽然这两个方案看上去是相反的，一个是在claude终端里对话控制飞书，另一个是在飞书里对话控制终端。

但实际上它们并不冲突。

CLI 让 Claude Code 能做事：管表格、发消息、出报表、查错误。

解决了“碰不到数据”的问题

Bridge 让 Claude Code 能随时对话：手机能用、记录保存、同事转手方便。

解决了“被困在终端里”的问题。

两个一装，Claude Code 从“只能坐在电脑前用的命令行工具”，变成了“随时在线、能读能写、能帮你干活的飞书同事”。

这两个方法打通了所有的流程，从今天起你可以顺畅丝滑的在飞书里用claude，并且用claude命令行控制飞书。

感谢你看到这里，如果你觉得有用，欢迎一键三连。下期见！

---------END--------

这里是【AI圈儿】，和一群人一起读懂AI。

欢迎+vx：KyroMa进入专属社群⭐