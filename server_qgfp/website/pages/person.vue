<template>
  <div>
    <div class="banner">
      <div class="content">
        <h1>加入我们，你将获得：</h1>
        <h3>完善的培训机制</h3>
        <p>为期1个月的系统化深入培训，领你走入投资世界。</p>
        <h3>学习交流空间</h3>
        <p>我们鼓励每一位伙伴踊跃参与讨论、分享观点，不断挑战自我边界。</p>
        <h3>向高效say hi，对 "dirty work" say bye</h3>
        <p>不写长篇累牍的报告，不做枯燥乏味的PPT，拒绝低效沟通。我们希望你做的工作都是对投资有价值的。</p>
      </div>
    </div>
    <div class="space bg">
      <div class="container">
        <h1 class="title">热招岗位</h1>
        <div class="list">
          <div class="item">
            <h2>行业研究员（实习）</h2>
            <h3>岗位职责：</h3>
            <p>学习理解量子星河投资理念，思考论证世界发展方向，寻找验证定价规律。</p>
            <p>参与会议，在会议中直接汇报核心信息与研究成果。</p>
            <p>你的研究和汇报会直接影响讨论结果，并可能最终应用于投资决策。</p>
            <h3>任职要求：</h3>
            <p>国内外知名高校本科及以上学历，欢迎非经济金融类专业投递；</p>
            <p>好奇世界发展规律、希望探索事物发展本质，善于独立思考、归纳总结；</p>
            <p>具有出色的逻辑思维能力和问题分析能力，有较强自驱力、沟通表达和团队协作能力，富有责任感和时间观念。</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "person",
  layout: 'layout'
}
</script>

<style lang="scss" scoped>
.banner {
  width: 100%;
  min-height: 580px;
  background: url("../assets/images/banner_5.jpg") no-repeat center bottom/cover;
  display: flex;
  align-items: center;
  justify-content: center;

  .content {
    max-width: 1000px;
    width: 100%;
    padding: 30px 50px;

    h1 {
      font-size: 40px;
      line-height: 56px;
      color: #FFFFFF;
      font-weight: initial;
      margin: 60px 0;
    }

    h3 {
      margin-top: 24px;
      font-weight: bold;
      font-size: 16px;
      line-height: 28px;
      color: #FFFFFF;
    }

    p {
      margin-top: 8px;
      font-size: 14px;
      line-height: 28px;
      color: #FFFFFF;
    }
  }
}

.bg {
  background: url("../assets/images/block_5.png") no-repeat center/cover;
}

.list {
  .item {
    color: #303030;

    h2 {
      font-size: 20px;
      line-height: 28px;
      margin-bottom: 24px;
      font-weight: initial;
    }

    h3 {
      font-size: 16px;
      line-height: 28px;
      margin-bottom: 8px;
      margin-top: 24px;
      font-weight: initial;
    }

    p {
      font-size: 14px;
      line-height: 28px;
      margin-bottom: 8px;
    }
  }
}

@media (max-width: 769px) {
  .banner {
    .content {
      padding: 30px;
    }
  }
}

@media (max-width: 641px) {
  .banner {
    .content {
      padding: 30px 20px;
    }
  }

}
</style>
