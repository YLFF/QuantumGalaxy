<template>
  <div>
    <div class="banner">
      <div class="content">
        <h1>关于我们</h1>
      </div>
    </div>
    <div class="space">
      <div class="container">
        <h1 class="title center">关于量子星河</h1>
        <div class="content">
          <p>量子星河成立于2020年12月，是一家迅速成长的<b>私募证券基金管理</b>公司。</p>
          <p>
            量子星河拥有完善的理论体系、灵敏的量化系统和成熟的投研团队支持，具备多策略、全市场的投资管理能力。借助我们独有的投研工具——星图，量子星河自上而下观察宏观大势、管理投资逻辑，自下而上敏锐响应市场、跟踪产业发展，致力于为投资者创造长期价值。</p>
        </div>
      </div>
    </div>
    <div class="space bg-1">
      <div class="container">
        <h1 class="title">创始人简介</h1>
        <div class="team">
          <div class="pic">
            <img src="../assets/images/team_1.jpg" alt="">
          </div>
          <div class="desc">
            <h2>张凌宇</h2>
            <h3>量子星河私募基金创始人，量子星河主架构师</h3>
            <ul>
              <li><b>清华大学</b>自动化系学士，<b>哥伦比亚大学</b>电子工程-神经科学方向硕士。</li>
              <li>2015-2016年就职于<b>中科院</b>自动化所脑科学组，从事类脑智能和模式识别项目研究。</li>
              <li>2016-2020年末就职于<b>工商银行总行</b>金融市场外汇衍生处，同时负责衍生品量化定价、高频外汇做市报价和打通金融市场和量化策略的交易系统，该项目于2020年荣获<b>《银行家》中国金融创新奖</b>。
              </li>
              <li><b>2020年12月，创立量子星河。</b></li>
            </ul>
          </div>
        </div>
        <div class="team">
          <div class="pic">
            <img src="../assets/images/team_2.jpg" alt="">
          </div>
          <div class="desc">
            <h2>姜一晨</h2>
            <h3>星河私募基金的创始合伙人，研究部主管负责人</h3>
            <ul>
              <li><b>北京大学</b>环境工程专业学士，<b>加州大学</b>洛杉矶分校金融工程硕士。</li>
              <li>就职于<b>国开金融投资部</b>。</li>
              <li>就职于<b>中信建投研究所</b>，积累了多年的从业经验，于顶级券商投研行业崭露头角。</li>
              <li><b>2020年12月，共同创立量子星河。</b></li>
            </ul>
          </div>
        </div>
      </div>
    </div>

    <div class="space bg-2">
      <el-row class="w100">
        <el-col :span="8" class="logo">
          <img src="../assets/images/logo_1.png" alt="">
        </el-col>
        <el-col :span="16" class="group">
          <el-col :span="11">
            <div class="group-item pointer">
              <img src="../assets/images/icon_1.png" alt="">
              <h3>求是</h3>
              <p>谨慎客观认知世界现状</p>
            </div>
          </el-col>
          <el-col :span="11">
            <div class="group-item pointer">
              <img src="../assets/images/icon_2.png" alt="">
              <h3>前瞻</h3>
              <p>大胆推演世界发展方向</p>
            </div>
          </el-col>
          <el-col :span="11">
            <div class="group-item pointer">
              <img src="../assets/images/icon_3.png" alt="">
              <h3>开放</h3>
              <p>乐于接受新事物并迅速建立认知</p>
            </div>
          </el-col>
          <el-col :span="11">
            <div class="group-item pointer">
              <img src="../assets/images/icon_4.png" alt="">
              <h3>全局观</h3>
              <p>使用自主开发的星图系统<br>用全局视角认识世界</p>
            </div>
          </el-col>
          <el-col :span="2">
          </el-col>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script>
export default {
  name: "about",
  layout: 'layout'
}
</script>

<style lang="scss" scoped>
.banner {
  width: 100%;
  height: 580px;
  background: url("../assets/images/banner_2.jpg") no-repeat center bottom/cover;
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
  }
}

.bg-1 {
  background: #FAFAFA;
}

.team {
  margin-bottom: 100px;
  padding-top: 20px;
  display: flex;
  align-items: center;

  &:last-child {
    margin-bottom: 0;
  }

  .pic {
    flex-shrink: 0;
    margin: 34px 93px 34px 40px;

    img {
      width: 210px;
      height: 210px;
      border-radius: 50%;
      display: block;
    }
  }

  .desc {

    h2 {
      font-weight: bold;
      font-size: 24px;
      line-height: 34px;
      color: #303030;
      margin-bottom: 8px;
    }

    h3 {
      font-weight: initial;
      font-size: 20px;
      line-height: 28px;
      color: #303030;
      margin-bottom: 40px;
    }

    ul {
      padding-left: 20px;

      li {
        font-size: 14px;
        line-height: 28px;
        color: #303030;

        b {
          font-weight: bold;
        }
      }
    }
  }
}

.bg-2 {
  background: url("../assets/images/block_2.jpg") no-repeat center/cover;

  .container {
    padding-top: 0;
    padding-bottom: 0;
  }
}

.logo {
  height: 660px;
  display: flex;
  justify-content: center;
  align-items: center;

  img {
    width: 200px;
    display: block;
  }
}

.group {
  background: rgba(255, 255, 255, 0.9);

  .group-item {
    height: 330px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-direction: column;
    transition: background-color 300ms;
    padding: 20px;

    img {
      width: 56px;
      height: 56px;
      display: block;
    }

    h3 {
      font-weight: bold;
      font-size: 20px;
      line-height: 28px;
      color: #303030;
      margin-top: 16px;
    }

    p {
      font-size: 16px;
      line-height: 22px;
      color: #303030;
      margin-top: 40px;
      min-height: 56px;
      text-align: center;
    }

    &:hover {
      background: rgba(255, 255, 255, 1);
    }
  }
}

@media (max-width: 769px) {
  .banner {
    .content {
      padding: 0 30px;
    }
  }

  .logo {
    height: 540px;
  }

  .group {
    .group-item {
      height: 270px;
    }
  }

  .team {
    .pic {
      margin: 34px 30px 34px 0;

      img {
        width: 160px;
        height: 160px;
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

  .el-col {
    width: 100%;
  }

  .logo {
    height: 270px;
  }

  .group {
    .group-item {
      height: 270px;
    }
  }

  .team {
    flex-direction: column;

    .pic {
      margin: 30px;

      img {
        width: 210px;
        height: 210px;
      }
    }

    .desc {
      h2 {
        text-align: center;
        margin: 40px 0;
      }
    }
  }
}
</style>
