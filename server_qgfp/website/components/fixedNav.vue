<template>
  <div class="tab" ref="navTab" :class="{'hide':hide}">
    <div class="tab-item pointer" v-for="(item, index) in tabList" :key="index" @click="scrollToPosition(index)"
         :class="{ 'is-active': active === index }">
      <h3>{{ item.name }}</h3>
      <div></div>
      <p>{{ item.desc }}</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'fixedNav',
  props: {
    tabList: {
      type: Array,
      default: () => []
    },
    navHeaderHeight: {
      type: Number,
      default: 0
    }
  },
  data() {
    return {
      active: 0,// 当前激活的导航索引
      hide: false,
      downAF: null,
      upAF: null,
    }
  },
  mounted() {
    this.onScroll()
    //监听页面滚动条事件
    window.addEventListener("scroll", this.onScroll);
  },
  beforeDestroy() {
    // 必须移除监听器，不然当该vue组件被销毁了，监听器还在就会出错
    window.removeEventListener("scroll", this.onScroll);
    this.clearAF()
  },
  methods: {
    clearAF() {
      if (this.downAF) {
        cancelAnimationFrame(this.downAF)
      }
      if (this.upAF) {
        cancelAnimationFrame(this.upAF)
      }
    },
    onScroll() {
      // 获取当前文档流的 scrollTop
      const scrollTop = document.documentElement.scrollTop || document.body.scrollTop

      if (scrollTop >= 60) {
        this.hide = true
      } else {
        this.hide = false
      }

      this.$nextTick().then(() => {
        let navTabHeight = this.$refs.navTab.offsetHeight //获取子导航的高度
        let navHeaderHeight = this.navHeaderHeight //获取悬浮导航的高度
        // 获取所有锚点元素
        let navContents = []
        this.tabList.forEach(item => {
          navContents.push(document.querySelectorAll(`.${item.class}`)[0])
        })
        // 所有锚点元素的 offsetTop
        let offsetTopArr = []
        navContents.forEach(item => {
          offsetTopArr.push(item.offsetTop)
        })

        // 定义当前点亮的导航下标
        let navIndex = 0
        for (let n = 0; n < offsetTopArr.length; n++) {
          // 如果 scrollTop 大于等于第 n 个元素的 offsetTop 则说明 n-1 的内容已经完全不可见
          // 那么此时导航索引就应该是 n 了
          if (scrollTop >= offsetTopArr[n] - navTabHeight - navHeaderHeight) {
            navIndex = n
          }
        }

        // 把下标赋值给 vue 的 data
        this.active = navIndex
      })

    },
    scrollToPosition(index) {
      let navTabHeight = this.$refs.navTab.offsetHeight //获取子导航的高度
      let navHeaderHeight = this.navHeaderHeight //获取悬浮导航的高度
      // 获取目标的 offsetTop
      // css选择器是从 1 开始计数，我们是从 0 开始，所以要 +1
      const targetOffsetTop = document.querySelector(`.${this.tabList[index].class}`).offsetTop - navTabHeight - navHeaderHeight
      // 获取当前 offsetTop
      let scrollTop = document.documentElement.scrollTop || document.body.scrollTop
      // 定义一次跳 50 个像素，数字越大跳得越快，但是会有掉帧得感觉，步子迈大了会扯到蛋
      const STEP = 50

      // 定义往下滑函数
      const smoothDown = () => {
        // 如果当前 scrollTop 小于 targetOffsetTop 说明视口还没滑到指定位置
        if (scrollTop < targetOffsetTop) {
          // 如果和目标相差距离大于等于 STEP 就跳 STEP
          // 否则直接跳到目标点，目标是为了防止跳过了。
          if (targetOffsetTop - scrollTop >= STEP) {
            scrollTop += STEP
          } else {
            scrollTop = targetOffsetTop
          }
          document.body.scrollTop = scrollTop
          document.documentElement.scrollTop = scrollTop
          // 屏幕在绘制下一帧时会回调传给 requestAnimationFrame 的函数
          // 关于 requestAnimationFrame 可以自己查一下，在这种场景下，相比 setInterval 性价比更高
          this.downAF = requestAnimationFrame(smoothDown)
        } else {
          this.clearAF()
        }
      }

      // 定义往上滑函数
      const smoothUp = () => {
        if (scrollTop > targetOffsetTop) {
          if (scrollTop - targetOffsetTop >= STEP) {
            scrollTop -= STEP
          } else {
            scrollTop = targetOffsetTop
          }
          document.body.scrollTop = scrollTop
          document.documentElement.scrollTop = scrollTop
          this.upAF = requestAnimationFrame(smoothUp)
        } else {
          this.clearAF()
        }
      }

      // 判断是往下滑还是往上滑
      if (scrollTop > targetOffsetTop) {
        // 往上滑
        smoothUp()
      } else {
        // 往下滑
        smoothDown()
      }
    },
  }
}
</script>
<style lang="scss" scoped>
.tab {
  width: 100%;
  display: flex;
  position: sticky;
  top: 60px;
  background: #00223A;
  z-index: 2;

  .tab-item {
    flex: 1;
    display: flex;
    align-items: center;
    flex-direction: column;
    color: #FFFFFF;
    padding: 20px 0;

    h3 {
      font-weight: bold;
      font-size: 16px;
      line-height: 28px;
      text-align: center;
    }

    div {
      height: 43px;
      display: flex;
      align-items: center;
      overflow: hidden;
      transition: height 200ms;

      &:before {
        content: "";
        display: block;
        width: 3px;
        height: 3px;
        border-radius: 50%;
        background: #ffffff;
      }
    }

    p {
      height: 28px;
      font-size: 14px;
      line-height: 28px;
      overflow: hidden;
      transition: height 200ms;
    }

    &.is-active {
      background: #003153;
    }
  }

  &.hide {
    .tab-item {
      div, p {
        height: 0;
      }

    }
  }
}


@media (max-width: 641px) {
  .tab {
    .tab-item {
      padding: 10px 0;
      h3 {
        font-size: 14px;
      }
      div, p {
        display: none;
      }
    }
  }

}
</style>
