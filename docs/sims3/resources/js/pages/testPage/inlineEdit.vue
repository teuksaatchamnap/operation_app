<template>
  <table>
    <tr v-for="(item, index) in items" :key="index">
      <td v-for="(field, colIndex) in fields" :key="colIndex" @dblclick="startEdit(index, colIndex)">
        <span v-if="editIndex !== index || editCol !== colIndex">
          {{ item[field] }}
        </span>
        <input v-else v-model="editValue" @blur="saveEdit(index, colIndex, field)"
          @keyup.enter="saveEdit(index, colIndex, field)" @keyup.esc="cancelEdit" ref="editInput" />
      </td>
    </tr>
  </table>
</template>

<script>
export default {
  data() {
    return {
      items: [
        { name: 'John', age: 25, city: 'New York' },
        { name: 'Jane', age: 30, city: 'London' }
      ],
      fields: ['name', 'age', 'city'],
      editIndex: null,
      editCol: null,
      editValue: ''
    }
  },
  methods: {
    startEdit(rowIndex, colIndex) {
      this.editIndex = rowIndex
      this.editCol = colIndex
      this.editValue = this.items[rowIndex][this.fields[colIndex]]
      this.$nextTick(() => {
        if (this.$refs.editInput) this.$refs.editInput.focus()
      })
    },
    saveEdit(rowIndex, colIndex, field) {
      this.items[rowIndex][field] = this.editValue
      this.editIndex = null
      this.editCol = null
    },
    cancelEdit() {
      this.editIndex = null
      this.editCol = null
    }
  }
}
</script>