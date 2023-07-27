<template>
  <div>
    <div class="banner">
      <div class="content">
        <img src="../assets/images/banner_text_1.png" alt="">
      </div>
    </div>
    <div class="space">
      <div class="container">
        <h1 class="title">量子星河简介</h1>
        <div class="content">
          <p>量子星河成立于2020年12月，是一家迅速成长的<b>私募证券基金管理</b>公司。</p>
          <p>
            量子星河拥有完善的理论体系、灵敏的量化系统和成熟的投研团队支持，具备多策略、全市场的投资管理能力。借助我们独有的投研工具——星图，量子星河自上而下观察宏观大势、管理投资逻辑，自下而上敏锐响应市场、跟踪产业发展，致力于为投资者创造长期价值。</p>
          <nuxt-link tag="div" class="arrow" to="/about">
            <img class="pointer" src="../assets/images/icon_arrow.png" alt="">
          </nuxt-link>
        </div>
      </div>
    </div>
    <div class="space bg">
      <div class="container">
        <h1 class="title">星河视界</h1>
        <div class="block">
          <el-row :gutter="35">
            <el-col :span="12">
              <a href="https://mp.weixin.qq.com/s/qUb5jB2VS5KUv15O53DqOA" target="_blank">
                <div class="item">
                  <div class="date">
                    <div class="month">05.25</div>
                    <div class="year">2022</div>
                  </div>
                  <div class="news">
                    <h2>夏虫语冰</h2>
                    <p>昨天是老张出生的第31个整年了，不由得要回忆回忆30年之间的日子都变化了…</p>
                  </div>
                </div>
              </a>
            </el-col>
            <el-col :span="12">
              <a href="https://mp.weixin.qq.com/s/9kIWi1505FXRy21vTJtT2Q" target="_blank">
                <div class="item">
                  <div class="date">
                    <div class="month">12.29</div>
                    <div class="year">2022</div>
                  </div>
                  <div class="news">
                    <h2>强美元的代价？人民币——给世界的备用选项</h2>
                    <p>美联储无尽头的加息、人民币汇率创新高、英国开启无限QE、各市场股债汇杀杀杀…</p>
                  </div>
                </div>
              </a>
            </el-col>
            <el-col :span="12">
              <a href="https://mp.weixin.qq.com/s/m5Y9LLDENxnxlPsv92njrg" target="_blank">
                <div class="item">
                  <div class="date">
                    <div class="month">01.01</div>
                    <div class="year">2023</div>
                  </div>
                  <div class="news">
                    <h2>2023年度全球宏观展望——秋风过耳，叶落如歌</h2>
                    <p>阵阵秋风、寒意袭来，引得轻嗽几声，四周环顾、叶落如歌。 「刍狗看万物」…</p>
                  </div>
                </div>
              </a>
            </el-col>
            <el-col :span="12">
              <nuxt-link tag="div" class="arrow" to="/galaxy">
                <img class="pointer" src="../assets/images/icon_arrow.png" alt="">
              </nuxt-link>
            </el-col>
          </el-row>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'IndexPage',
  layout: 'layout'
}
</script>

<style lang="scss" scoped>
.banner {
  width: 100%;
  height: 580px;
  background: url("../assets/images/banner_1.jpg") no-repeat center bottom/cover;
  display: flex;
  align-items: center;
  justify-content: center;

  .content {
    max-width: 1000px;
    width: 100%;
    padding: 0 50px;

    img {
      max-width: 589px;
      width: 100%;
      display: block;
      margin: 0 auto;
    }
  }
}

.bg {
  background: url("../assets/images/block_1.png") no-repeat center/cover;
}

.block {
  display: flex;
  flex-wrap: wrap;

  .item {
    margin: 20px 0;
    padding: 30px 60px 30px 30px;
    background: #ffffff;
    display: flex;
    width: 100%;

    .date {
      margin-right: 40px;
      height: 75px;
      border-bottom: 1px solid #BABABA;
      flex-shrink: 0;

      .month {
        font-size: 20px;
        line-height: 28px;
        color: #303030;
      }

      .year {
        font-size: 12px;
        line-height: 14px;
        color: #BABABA;
        margin-top: 3px;
      }
    }

    .news {
      h2 {
        font-weight: initial;
        font-size: 15px;
        line-height: 21px;
        color: #303030;
        margin-bottom: 16px;
        min-height: 42px;
      }

      p {
        font-size: 13px;
        line-height: 18px;
        color: #BABABA;
      }
    }
  }

  .arrow {
    margin-top: 80px;
  }
}

@media (max-width: 769px) {
  .banner {
    .content {
      padding: 0 30px;
    }
  }
}

@media (max-width: 641px) {

  .el-col-12 {
    width: 100%;

    .arrow {
      margin-top: 0;
    }
  }
}
</style>
