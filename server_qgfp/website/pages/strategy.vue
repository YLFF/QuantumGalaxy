<template>
  <div>
    <div class="banner">
      <div class="content">
        <h1>管理理念</h1>
        <p>看懂世界·管好仓位</p>
      </div>
    </div>
    <fixedNav :tab-list="tabList" :nav-header-height="navHeaderHeight"/>
    <div class="space">
      <div class="container">
        <h1 class="title">投研方法</h1>
        <div class="content">
          <p>借助星图系统，观察宏观大势、跟踪产业发展、执行微观交易</p>
        </div>
        <div>

          <div class="content-block left-pic tab-content-1">
            <div class="img">
              <img src="../assets/images/content_1.jpg" alt="">
            </div>
            <div class="text">
              <h2>星图</h2>
              <p>将世界上的实时经济活动抽象成一张联通千行百业的经济网络，犹如星辰不断汇聚成星座。这就是量子星河的专属方法论——星图。我们观察星图闪烁，记录每时每刻行业跃迁的能量波动。</p>
              <h3>数据积累，托举投资视野</h3>
              <p>囊括各行各业的上市公司的产品服务、指标数据等近万节点。</p>
              <h3>可视化分析，奠基决策高度</h3>
              <p>产业链、供需差、库存量等内容高度可视化。</p>
            </div>
          </div>

          <div class="content-block right-pic tab-content-2">
            <div class="text">
              <h2>世界线</h2>
              <p>我们从生产要素的供需变化，来认识宏观现象的发生，及背后的经济逻辑，以挖掘行业性的投资机会。通过谨慎推敲，对预期影响久远、反应相对剧烈的逻辑，进行认知、梳理和汇总。星辰指导我们投资决策的路径
                ——世界线。</p>
              <p><b>产业链交织的巨大蛛网，每一次颤动，都会改变网中资金水珠的流动和流向。我们的世界线，是对蛛丝的精确感触。</b></p>
            </div>
            <div class="img">
              <img src="../assets/images/content_2.jpg" alt="">
            </div>
          </div>

          <div class="content-block left-pic tab-content-3">
            <div class="img">
              <img src="../assets/images/content_3.jpg" alt="">
            </div>
            <div class="text">
              <h2>量化系统</h2>
              <h3>系统管理 </h3>
              <p>使用量子星河智能资管系统表达全部投资观点，做好仓位管理和风险控制，将投资机会落实为收益。</p>
              <h3>实时响应</h3>
              <p>实时构建出兼具更高投资确定性和回报率的持仓组合。在全球金融市场高效开展资产管理，力图为投资者带来可观的回报。</p>
            </div>
          </div>

          <div class="content-block right-pic tab-content-4">
            <div class="text">
              <h2>透明管理</h2>
              <p>量子星河致力于打造白盒策略，打破传统信息差。我们将以周报形式汇总新认知，分享给每一位投资人。</p>
              <h3>宏观经济概述</h3>
              <p>设色思维导图呈现经济事件的发展程度与重要性评估。</p>
              <h3>投资标的解读</h3>
              <p>精选投资观点，详解相关标的与对应量化分析。</p>
            </div>
            <div class="img">
              <img src="../assets/images/content_4.jpg" alt="">
            </div>
          </div>

        </div>
      </div>
    </div>

    <div class="space">
      <div class="container">
        <h1 class="title center">风控原则</h1>
        <div class="principle">
          <el-row>
            <el-col :span="8">
              <div class="principle-item">
                <h2>多元配置</h2>
                <p>实施多元多区域资产配置，有效对冲风险。</p>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="principle-item border-l-r">
                <h2>分散投资</h2>
                <p>严格限制对行业和个股的投资集中度，通过分散投资控制组合风险。</p>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="principle-item">
                <h2>灵活策略</h2>
                <p>灵活应用选股策略、择时策略和衍生品策略等，根据市场环境调整投资策略。</p>
              </div>
            </el-col>
          </el-row>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
import fixedNav from "~/components/fixedNav.vue";

export default {
  name: "strategy",
  layout: 'layout',
  components: {fixedNav},
  data() {
    return {
      tabList: [
        {name: "星图", desc: "积累宏观认知", class: "tab-content-1"},
        {name: "世界线", desc: "归纳市场动向", class: "tab-content-2"},
        {name: "量化系统", desc: "系统实时响应", class: "tab-content-3"},
        {name: "透明管理", desc: "共享投资信息", class: "tab-content-4"},
      ],
      navHeaderHeight: 60,
    }
  }
}
</script>

<style lang="scss" scoped>
.banner {
  width: 100%;
  height: 580px;
  background: url("../assets/images/banner_3.jpg") no-repeat center bottom/cover;
  display: flex;
  align-items: center;
  justify-content: center;

  .content {
    max-width: 1000px;
    width: 100%;
    padding: 0 50px;

    h1 {
      font-size: 40px;
      line-height: 56px;
      color: #FFFFFF;
      font-weight: initial;
    }

    p {
      font-size: 20px;
      line-height: 28px;
      color: #FFFFFF;
      margin-top: 8px;
    }
  }
}

.content-block {
  display: flex;
  align-items: center;
  margin-bottom: 40px;
  padding: 20px 0;

  &.left-pic {
    .img {
      flex-shrink: 0;
      margin-right: 60px;

      img {
        width: 330px;
        height: 423px;
        display: block;
      }
    }
  }

  .text {
    h2 {
      font-weight: bold;
      font-size: 24px;
      line-height: 28px;
      color: #303030;
      margin-bottom: 16px;
    }

    h3 {
      font-weight: bold;
      font-size: 16px;
      line-height: 28px;
      color: #303030;
      margin-bottom: 8px;
      margin-top: 16px;
    }

    p {
      font-size: 14px;
      line-height: 28px;
      color: #303030;

      b {
        font-weight: bold;
      }
    }
  }

  &.right-pic {
    .img {
      flex-shrink: 0;
      margin-left: 60px;

      img {
        width: 449px;
        height: 330px;
        display: block;
      }
    }
  }

  &:first-child {
    margin-top: 40px;

    &.left-pic {
      align-items: flex-start;
    }
  }

  &:last-child {
    margin-bottom: 0;
    padding-bottom: 0;

    &.right-pic {
      align-items: flex-end;
    }
  }
}

.principle {
  margin-top: 60px;
  background: url("../assets/images/block_3.jpg") no-repeat center/cover;

  .principle-item {
    height: 360px;
    color: #ffffff;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    padding: 50px;

    &.border-l-r {
      border-left: 1px solid #D9D9D9;
      border-right: 1px solid #D9D9D9;
    }

    h2 {
      font-weight: initial;
      font-size: 24px;
      line-height: 34px;
      padding-bottom: 20px;
      border-bottom: 1px solid #ffffff;
      width: 100%;
      text-align: center;
    }

    p {
      font-size: 14px;
      line-height: 28px;
      margin-top: 20px;
      min-height: 84px;
    }
  }
}


@media (max-width: 769px) {
  .banner {
    .content {
      padding: 0 30px;
    }
  }

  .content-block {
    &.left-pic {
      .img {
        margin-right: 40px;

        img {
          width: 270px;
          height: 345px;
        }
      }
    }

    &.right-pic {
      .img {
        margin-left: 40px;

        img {
          width: 336px;
          height: 270px;
          display: block;
        }
      }
    }
  }
}


@media (max-width: 641px) {
  .banner {
    .content {
      padding: 0 20px;
    }
  }

  .content-block {
    flex-direction: column;
    align-items: flex-start;
    margin-bottom: 0;
    padding: 20px 0;

    &.left-pic {
      .img {
        margin-right: 0;

        img {
          width: 100%;
          height: auto;
        }
      }
    }

    .text {
      margin: 20px 0;
    }

    &.right-pic {
      .img {
        margin-left: 0;
        order: 0;

        img {
          width: 100%;
          height: auto;
        }
      }

      .text {
        order: 1;
      }


    }

    &:first-child {
      margin-top: 0;

      &.left-pic {
        align-items: flex-start;
      }
    }

    &:last-child {
      margin-bottom: 0;
      padding-bottom: 0;

      &.right-pic {
        align-items: flex-start;
      }
    }
  }

  .el-col-8 {
    width: 100%;
  }

  .principle {
    .principle-item {
      height: 260px;
      padding: 30px 20px;

      &.border-l-r {
        border-left: none;
        border-right: none;
        border-top: 1px solid #D9D9D9;
        border-bottom: 1px solid #D9D9D9;
      }
    }
  }
}

</style>
