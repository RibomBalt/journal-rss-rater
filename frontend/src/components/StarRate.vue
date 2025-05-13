<template>
    <div class="root">
        <div class="star-wrap bottom">
            <span></span>
            <span></span>
            <span></span>
            <span></span>
            <span></span>
        </div>
        <div class="star-wrap mask">
            <div style="width:300px">
                <span></span>
                <span></span>
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { computed, defineModel } from 'vue';

const score = defineModel<number | null>();

const score_width = computed(() => {
    const score_value = score.value ?? 0;
    return (score_value / 5 * 100).toString() + '%';
});

</script>


<style scoped>
.root {
    position: relative;
    display: inline-block;
    min-width: 96px;
}

.star-wrap span {
    float: left;
    width: 16px;
    height: 16px;
}

.star-wrap span:not(:last-child) {
    margin-right: 4px;
}

.bottom span {
    background: url(./../assets/star-gray.svg) 0 0 no-repeat;
}

.mask span {
    background: url(./../assets/star-color.svg) 0 0 no-repeat;
}

.mask {
    position: absolute;
    left: 0;
    top: 0;
    overflow: hidden;
    width: v-bind(score_width);
}
</style>