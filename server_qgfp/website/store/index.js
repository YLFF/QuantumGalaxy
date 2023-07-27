import Vue from "vue"
import Vuex from "vuex"

Vue.use(Vuex)

const state = ()=>(
  {
    dialogVisible: true
  }
)
const getters =  {
  dialogVisible: state => state.dialogVisible,
}

const mutations =  {
  changeDialogVisible(state, data) {
    state.dialogVisible = data
  }
}

const actions =  {
  changeDialogVisible({commit}, data) {
    commit("changeDialogVisible", data)
  }
}

export default {
  state,
  getters,
  mutations,
  actions,

}
