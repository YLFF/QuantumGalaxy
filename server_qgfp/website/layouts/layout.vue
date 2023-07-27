<template>
  <div class="page">
    <header :class="headerClass">
      <div class="header-content">
        <nuxt-link class="logo pointer" tag="div" to="/">
          <img src="../assets/images/header_logo.png" alt="">
        </nuxt-link>
        <ul class="nav">
          <nuxt-link tag="li" to="/">首页</nuxt-link>
          <nuxt-link tag="li" to="/about">关于我们</nuxt-link>
          <nuxt-link tag="li" to="/strategy">投资策略</nuxt-link>
          <nuxt-link tag="li" to="/galaxy">星河视界</nuxt-link>
          <nuxt-link tag="li" to="/person">人才计划</nuxt-link>
          <nuxt-link tag="li" to="/customers">客户中心</nuxt-link>
        </ul>
        <div class="menu" @click="menu = true">
          <i class="el-icon-menu"></i>
        </div>
      </div>
    </header>
    <nuxt></nuxt>
    <footer>
      <div class="footer-content">
        <h3>量子星河（上海）私募基金管理有限公司</h3>
        <div>邮箱：<a href="mailto:ir@quantumgalaxy.cn">ir@quantumgalaxy.cn</a></div>
        <div>微信：QuantumGalaxyGroup</div>
        <div>公司地址：北京市西城区金融街丰汇时代大厦东翼705</div>
        <p>本网站所有内容仅供参考，如有与本公司相关公告及基金法律文件不符，以相关公告及基金法律文件为准。市场有风险，投资需谨慎。</p>
        <p><a href="http://beian.miit.gov.cn/publish/query/indexFirst.action" rel="noreferrer" target="_blank">京ICP备2022004209号-1</a><span class="interval">基金业协会登记编号：P1022718</span></p>
      </div>
    </footer>
    <el-backtop></el-backtop>
    <el-drawer
      :visible.sync="menu"
      size="60%"
      :with-header="false"
    >
      <ul class="mobile-nav" @click="menu = false">
        <nuxt-link tag="li" to="/">首页</nuxt-link>
        <nuxt-link tag="li" to="/about">关于我们</nuxt-link>
        <nuxt-link tag="li" to="/strategy">投资策略</nuxt-link>
        <nuxt-link tag="li" to="/galaxy">星河视界</nuxt-link>
        <nuxt-link tag="li" to="/person">人才计划</nuxt-link>
        <nuxt-link tag="li" to="/customers">客户中心</nuxt-link>
      </ul>
    </el-drawer>

    <el-dialog
      title="投资者承诺"
      :visible.sync="dialogVisible"
      width="80%" center
      :show-close="false">
      <div class="dialog-content">
        <p>在继续浏览本公司网站前，请您确认您或您所代表的机构是一名<b>“合格投资者”。“合格投资者”</b>指根据任何国家和地区的证券和投资法规所规定的有资格投资于私募证券投资基金的专业投资者。例如根据我国《私募投资基金监督管理暂行办法》的规定，合格投资者的标准如下：
        </p>

        <p>一、具备相应风险识别能力和风险承担能力，投资于单只私募基金的金额不低于100万元且符合下列相关标准的单位和个人 <br>
          1、净资产不低于1000万元的单位；<br>
          2、金融资产不低于300万元或者最近三年个人年均收入不低于50万元的个人。(前款所称金融资产包括银行存款、股票、债券、基金份额、资产管理计划、银行理财产品、信托计划、保险产品、期货权益等。)</p>

        <p>二、下列投资者视为合格投资者： <br>
          1、社会保障基金、企业年金等养老基金、慈善基金等社会公益基金；<br>
          2、依法设立并在基金业协会备案的投资计划；<br>
          3、投资于所管理私募基金的私募基金管理人及其从业人员；<br>
          4、中国证监会规定的其他投资者。</p>

        <p>
          如果您继续访问或使用本网站及其所载资料，即表明您声明及保证您或您所代表的机构为“合格投资者”，并将遵守对您适用的司法区域的有关法律及法规，同意并接受以下条款及相关约束。如果您不符合“合格投资者”标准或不同意下列条款及相关约束，请勿继续访问或使用本网站及其所载信息及资料。</p>

        <p>
          投资涉及风险，投资者应详细审阅产品的发售文件以获取进一步资料，了解有关投资所涉及的风险因素，并寻求适当的专业投资和咨询意见。产品净值及其收益存在涨跌可能，过往的产品业绩数据并不预示产品未来的业绩表现。本网站所提供的资料并非投资建议或咨询意见，投资者不应依赖本网站所提供的信息及资料作出投资决策。</p>
      </div>
      <div slot="footer" class="dialog-footer">
        <el-button type="primary" @click="$store.dispatch('changeDialogVisible',false)">确定</el-button>
        <el-button type="primary" @click="$store.dispatch('changeDialogVisible',false)">取消</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
export default {
  name: "layout",
  data() {
    return {
      headerClass: "",
      menu: false,
    }
  },
  computed:{
    dialogVisible(){
      return this.$store.getters.dialogVisible
    }
  },
  mounted() {
    this.handleScroll()
    window.addEventListener('scroll', this.handleScroll) // 监听页面滚动
  },
  beforeDestroy() {
    window.removeEventListener('scroll', this.handleScroll)
  },
  methods: {
    handleScroll() {
      let scrollTop = window.pageYOffset || document.documentElement.scrollTop || document.body.scrollTop
      // 设置背景颜色的透明度
      if (scrollTop > 60) {
        this.headerClass = 'fixed' // scrollTop + 多少根据自己的需求设置
      } else if (scrollTop === 0) {
        this.headerClass = '' // 设置回到顶部时，背景颜色为透明
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.page {
  header {
    height: 60px;
    transition: background-color 300ms;
    width: 100%;
    display: flex;
    justify-content: center;
    position: fixed;
    top: 0;
    left: 0;
    z-index: 100;

    .header-content {
      max-width: 1000px;
      width: 100%;
      display: flex;
      justify-content: space-between;

      .logo {
        flex-shrink: 0;

        img {
          width: auto;
          height: 60px;
          display: block;
        }
      }

      .nav {
        display: flex;

        li {
          flex-shrink: 0;
          list-style: none;
          display: flex;
          align-items: center;
          padding: 20px 30px;
          cursor: pointer;
          color: #ffffff;
          transition: background-color, padding 300ms;

          &:hover {
            background-color: #003153;
          }

          &.nuxt-link-exact-active {
            background-color: #003153;
          }
        }
      }
    }

    &.fixed {
      background-color: #003153;

      .header-content {
        .nav {
          li {

            &:hover {
              color: #003153;
              background-color: #ffffff;
            }

            &.nuxt-link-exact-active {
              color: #003153;
              background-color: #ffffff;
            }
          }
        }
      }
    }
  }

  footer {
    display: flex;
    justify-content: center;
    width: 100%;
    background: url("../assets/images/footer.jpg") no-repeat center/cover;

    .footer-content {
      max-width: 1000px;
      width: 100%;
      padding: 40px 50px 50px 50px;
      color: #ffffff;
      line-height: 1.4;

      h3 {
        font-size: 16px;
        font-weight: normal;
        margin-bottom: 16px;
      }

      div {
        font-size: 14px;
        margin: 4px 0;

        & + p {
          margin-top: 16px;
        }
      }

      p {
        font-size: 12px;
        margin: 4px 0;
      }

      .interval {
        margin-left: 30px;
      }
    }
  }

  /deep/
  .el-backtop {
    i {
      font-size: 24px;
      color: #003153;
    }
  }
}

.menu {
  display: none;
}

.mobile-nav {
  li {
    flex-shrink: 0;
    list-style: none;
    display: flex;
    align-items: center;
    padding: 20px 30px;
    cursor: pointer;
    color: #003153;
    transition: background-color, padding 300ms;

    &.nuxt-link-exact-active {
      color: #ffffff;
      background-color: #003153;
    }
  }
}

/deep/
.el-dialog {
  max-width: 1000px;
}

.dialog-content {
  p {
    font-size: 14px;
    line-height: 28px;
    color: #000000;
    margin-bottom: 28px;

    b {
      font-weight: bold;
    }
  }
}

.dialog-footer {
  .el-button {
    background: #003153;
    border-color: #003153;
    width: 100px;

    & + .el-button {
      margin-left: 30px;
    }
  }
}

@media (max-width: 860px) {
  .page header .header-content .nav li {
    padding: 20px 20px;
  }
}

@media (max-width: 769px) {
  .page {
    footer {
      .footer-content {
        padding: 40px 30px 50px 30px;
      }
    }
  }
}

@media (max-width: 720px) {
  .page {
    header {
      .header-content {
        .nav {
          display: none;
        }
      }
    }
  }

  .menu {
    width: 60px;
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #ffffff;
    font-size: 30px;
  }
}


@media (max-width: 641px) {
  .page {
    footer {
      .footer-content {
        padding: 40px 20px;
      }
    }
  }
}
</style>
