<template>
  <div class="space bg">
    <div class="content">
      <p>查看产品及服务请联系小助手出具合格投资者证明</p>
      <h1>联系我们</h1>
      <div>
        <p>邮箱：<a href="mailto:ir@quantumgalaxy.cn">ir@quantumgalaxy.cn</a></p>
        <p>微信：QuantumGalaxyGroup</p>
        <p>公司地址：北京市西城区金融街丰汇时代大厦东翼705</p>
      </div>
    </div>
    <div class="footer">
      <p>本网站所有内容仅供参考，如有与本公司相关公告及基金法律文件不符，以相关公告及基金法律文件为准。市场有风险，投资需谨慎。</p>
      <p><a href="http://beian.miit.gov.cn/publish/query/indexFirst.action" rel="noreferrer" target="_blank">京ICP备2022004209号-1</a><span class="interval">基金业协会登记编号：P1022718</span></p>
    </div>
  </div>
</template>

<script>
export default {
  name: "customers",
  layout: 'layout2'
}
</script>

<style lang="scss" scoped>
.bg {
  width: 100%;
  min-height: 100vh;
  background: url("../assets/images/banner_6.jpg") no-repeat center bottom/cover;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.content {
  max-width: 1000px;
  width: 100%;
  padding: 160px 50px;
  flex: 1;
  display: flex;
  flex-direction: column;

  p {
    font-size: 20px;
    line-height: 28px;
    margin: 16px 0;
    color: #ffffff;
  }

  h1 {
    font-size: 40px;
    line-height: 56px;
    color: #FFFFFF;
    margin-top: 24px;
    margin-bottom: 60px;
  }
}

.footer {
  padding: 50px;
  max-width: 1000px;
  width: 100%;
  line-height: 1.4;

  p {
    font-size: 12px;
    color: #FFFFFF;
    margin: 4px 0;
  }

  .interval {
    margin-left: 30px;
  }
}

@media (max-width: 769px) {
  .content {
    padding: 100px 30px;
  }
  .footer {
    padding: 30px;
  }
}
</style>
